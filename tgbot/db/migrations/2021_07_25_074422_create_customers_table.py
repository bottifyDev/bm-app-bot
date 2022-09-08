from orator.migrations import Migration

class CreateCustomersTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('customers') as table:
            table.increments('id')
            table.string('uid').unique()
            table.string('name')
            table.float('balance')
            table.boolean('banned').default(False)
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('customers')
