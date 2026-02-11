const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

// PostgreSQL configuration
const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER || 'postgres',
  password: '7646',
  database: process.env.DB_NAME || 'gomums',
});

async function applyMigration() {
  const client = await pool.connect();
  
  try {
    console.log('Connected to PostgreSQL database\n');
    
    // Read the migration file
    const migrationPath = path.join(__dirname, '../../alembic/add_recipe_steps.sql');
    const sql = fs.readFileSync(migrationPath, 'utf-8');
    
    console.log('Applying migration: add_recipe_steps.sql\n');
    
    // Execute the migration
    await client.query(sql);
    
    console.log('✅ Migration applied successfully!');
    console.log('   - Added steps column (JSONB)');
    console.log('   - Created GIN index on steps');
    console.log('   - Backfilled existing instructions into steps');
    
  } catch (error) {
    console.error('❌ Error applying migration:', error.message);
    throw error;
  } finally {
    client.release();
  }
}

// Run the migration
applyMigration()
  .then(() => {
    console.log('\n✨ Migration completed successfully');
    pool.end();
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n❌ Migration failed:', error);
    pool.end();
    process.exit(1);
  });
