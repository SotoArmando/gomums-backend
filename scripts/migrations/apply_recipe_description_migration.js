const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'gomums',
  user: 'postgres',
  password: '7646'
});

async function applyMigration() {
  try {
    console.log('Connected to PostgreSQL database\n');
    
    // Read the migration file
    const migrationPath = path.join(__dirname, '..', '..', 'alembic', 'add_recipe_description.sql');
    const migrationSQL = fs.readFileSync(migrationPath, 'utf8');
    
    console.log('Applying migration: add_recipe_description.sql\n');
    
    // Execute the migration
    await pool.query(migrationSQL);
    
    console.log('✅ Migration applied successfully!');
    console.log('   - Added description column (TEXT)\n');
    
    // Verify the column exists
    const result = await pool.query(`
      SELECT column_name, data_type, is_nullable 
      FROM information_schema.columns 
      WHERE table_name = 'recipes' AND column_name = 'description'
    `);
    
    if (result.rows.length > 0) {
      console.log('✅ Verification successful:');
      console.log(`   Column: ${result.rows[0].column_name}`);
      console.log(`   Type: ${result.rows[0].data_type}`);
      console.log(`   Nullable: ${result.rows[0].is_nullable}`);
    }
    
    console.log('\n✨ Migration completed successfully\n');
    
  } catch (error) {
    console.error('❌ Migration failed:', error.message);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

applyMigration();
