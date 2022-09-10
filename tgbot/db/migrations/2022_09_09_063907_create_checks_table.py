from orator.migrations import Migration


class CreateChecksTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('checks') as table:
            table.increments('id')
            table.integer('crm_id')
            table.integer('count').default(0)
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('checks')
