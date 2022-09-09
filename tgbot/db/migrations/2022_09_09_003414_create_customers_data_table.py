from orator.migrations import Migration


class CreateCustomersDataTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('customers_data') as table:
            table.increments('id')
            table.integer('customer_id').unsigned()
            table.foreign('customer_id').references('id').on('customers').on_delete('cascade')
            table.integer('category').default(0)
            table.string('login').nullable()
            table.integer('crm_id').default(0)
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('customers_data')
