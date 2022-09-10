from orator.migrations import Migration


class CreateCheckConfigTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('check_config') as table:
            table.increments('id')
            table.integer('period').default(60)
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('check_config')
