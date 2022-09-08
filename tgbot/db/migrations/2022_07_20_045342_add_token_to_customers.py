from orator.migrations import Migration


class AddTokenToCustomers(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('customers') as table:
            table.string('token').nullable()

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('customers') as table:
            pass
