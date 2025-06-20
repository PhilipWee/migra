from __future__ import unicode_literals

from typing import List

from schemainspect import DBInspector, get_inspector

from .changes import Changes
from .statements import Statements


class Migration(object):
    """
    The main class of migra
    """

    def __init__(
        self,
        x_from,
        x_target,
        schema=None,
        exclude_schemas: List[str] = [],
        ignore_extension_versions=False,
    ):
        self.statements = Statements()
        self.changes = Changes(None, None)
        if schema and len(exclude_schemas) > 0:
            raise ValueError("You cannot have both a schema and excluded schema")
        self.schema = schema
        self.exclude_schema = exclude_schemas
        if isinstance(x_from, DBInspector):
            self.changes.i_from = x_from
        else:
            self.changes.i_from = get_inspector(
                x_from, schema=schema, exclude_schemas=exclude_schemas
            )
            if x_from:
                self.s_from = x_from
        if isinstance(x_target, DBInspector):
            self.changes.i_target = x_target
        else:
            self.changes.i_target = get_inspector(
                x_target, schema=schema, exclude_schemas=exclude_schemas
            )
            if x_target:
                self.s_target = x_target

        self.changes.ignore_extension_versions = ignore_extension_versions

    def inspect_from(self):
        self.changes.i_from = get_inspector(
            self.s_from, schema=self.schema, exclude_schemas=self.exclude_schema
        )

    def inspect_target(self):
        self.changes.i_target = get_inspector(
            self.s_target, schema=self.schema, exclude_schemas=self.exclude_schema
        )

    def clear(self):
        self.statements = Statements()

    def apply(self):
        from sqlbag import raw_execute

        for stmt in self.statements:
            raw_execute(self.s_from, stmt)
        self.changes.i_from = get_inspector(
            self.s_from, schema=self.schema, exclude_schemas=self.exclude_schema
        )
        safety_on = self.statements.safe
        self.clear()
        self.set_safety(safety_on)

    def add(self, statements):
        self.statements += statements

    def add_sql(self, sql):
        self.statements += Statements([sql])

    def set_safety(self, safety_on):
        self.statements.safe = safety_on

    def add_extension_changes(self, creates=True, drops=True):
        if creates:
            self.add(self.changes.extensions(creations_only=True))
        if drops:
            self.add(self.changes.extensions(drops_only=True))

    def add_all_changes(self, privileges=False):
        self.add(self.changes.schemas(creations_only=True))

        self.add(self.changes.extensions(creations_only=True, modifications=False))
        self.add(self.changes.extensions(modifications_only=True, modifications=True))
        self.add(self.changes.collations(creations_only=True))
        self.add(self.changes.enums(creations_only=True, modifications=False))

        self.add(self.changes.sequences(creations_only=True))
        self.add(self.changes.comments(drops_only=True, modifications=False))
        self.add(self.changes.triggers(drops_only=True))
        self.add(self.changes.rlspolicies(drops_only=True))
        if privileges:
            self.add(self.changes.privileges(drops_only=True))
        self.add(self.changes.non_pk_constraints(drops_only=True))

        self.add(self.changes.mv_indexes(drops_only=True))
        self.add(self.changes.non_table_selectable_drops())

        self.add(self.changes.pk_constraints(drops_only=True))
        self.add(self.changes.non_mv_indexes(drops_only=True))

        self.add(self.changes.tables_only_selectables())

        self.add(self.changes.sequences(drops_only=True))
        self.add(self.changes.enums(drops_only=True, modifications=False))
        self.add(self.changes.extensions(drops_only=True, modifications=False))
        self.add(self.changes.non_mv_indexes(creations_only=True))
        self.add(self.changes.pk_constraints(creations_only=True))
        self.add(self.changes.non_pk_constraints(creations_only=True))

        self.add(self.changes.non_table_selectable_creations())
        self.add(self.changes.mv_indexes(creations_only=True))

        if privileges:
            self.add(self.changes.privileges(creations_only=True))
        self.add(self.changes.rlspolicies(creations_only=True))
        self.add(self.changes.triggers(creations_only=True))
        self.add(self.changes.comments(creations_only=True))
        self.add(self.changes.collations(drops_only=True))
        self.add(self.changes.schemas(drops_only=True))

    @property
    def sql(self):
        return self.statements.sql
