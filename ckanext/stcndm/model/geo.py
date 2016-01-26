#!/usr/bin/env python
# encoding: utf-8
from logging import getLogger

from sqlalchemy import Table, types, ForeignKey, Column, sql

from ckan import model
from ckanapi import LocalCKAN

logger = getLogger(__name__)


geodescriptor_table = Table(
    'geodescriptor',
    model.meta.metadata,
    Column('id', types.Integer, primary_key=True),
    # The UUID of the related dataset package.
    Column('package_id', types.UnicodeText, ForeignKey('package.id')),
    # The UUID of the related geodescriptor package.
    Column('geo_id', types.UnicodeText, ForeignKey('package.id'))
)


def setup():
    # Workaround for aggressive postgres table locking.
    model.Session.close()

    if not geodescriptor_table.exists():
        try:
            geodescriptor_table.create()
        except Exception as e:
            if geodescriptor_table.exists():
                # Make sure we clean up a partially-created table.
                geodescriptor_table.drop()

            raise e

        logger.debug('Geodescriptor association table created.')
    else:
        logger.debug('Geodescriptor association table already exists.')


def update_relationship(package_id, geodescriptor_code):
    """
    Associate the geodescriptor given by `geodescriptor_code` with the
    dataset referenced by `package_id`, which is a product_id_new.

    :param package_id:The product_id_new of the dataset.
    :type package_id: unicode
    """
    lc = LocalCKAN()

    pkg = lc.action.package_search(
        q='product_id_new:{pid}'.format(
            pid=package_id
        ),
        rows=1
    )

    geo = lc.action.package_search(
        q='geodescriptor_code:{geo}'.format(
            geo=geodescriptor_code
        ),
        rows=1
    )

    if pkg['results'] and geo['results']:
        pkg = pkg['results'][0]
        geo = geo['results'][0]
    else:
        # FIXME: Should we raise?
        return

    s = model.Session.execute(
        sql.select([geodescriptor_table.c.id]).where(
            sql.and_(
                geodescriptor_table.c.package_id == pkg['id'],
                geodescriptor_table.c.geo_id == geo['id']
            )
        )
    )

    # FIXME: Use exists()?
    if s.rowcount:
        # The relationship already exists, nothing to do.
        return

    model.Session.execute(
        geodescriptor_table.insert().values(
            package_id=pkg['id'],
            geo_id=geo['id']
        )
    )

    model.Session.commit()


def get_geodescriptors_for_package(package_id):
    """
    Yield all of the geodescriptor package IDs that are associated with
    the ID given in `package_id` (which is a product_id_new).

    :param package_id: The product_id_new of the dataset to lookup.
    :type package_id: unicode
    """
    lc = LocalCKAN()

    pkg = lc.action.package_search(
        q='product_id_new:{pid}'.format(
            pid=package_id
        ),
        rows=1
    )

    if pkg['results']:
        pkg = pkg['results'][0]
    else:
        return

    s = model.Session.execute(
        sql.select([
            geodescriptor_table.c.geo_id
        ]).where(
            geodescriptor_table.c.package_id == pkg['id']
        )
    )

    for geo_id in s:
        yield geo_id[0]


def clear_geodescriptors_for_package(package_id):
    """
    Erase all geodescriptor associations from the given `package_id`
    (which is a package_id_new).

    :param package_id: The product_id_new of the dataset to clear.
    :type package_id: unicode
    """
    lc = LocalCKAN()

    pkg = lc.action.package_search(
        q='product_id_new:{pid}'.format(
            pid=package_id
        ),
        rows=1
    )

    if pkg['results']:
        pkg = pkg['results'][0]
    else:
        return 0

    return model.Session.execute(
        geodescriptor_table.delete().where(
            geodescriptor_table.c.package_id == pkg['id']
        )
    ).rowcount
