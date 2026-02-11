const { Pool } = require('pg');

// PostgreSQL configuration
const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER || 'postgres',
  password: '7646',
  database: process.env.DB_NAME || 'gomums',
});

async function clearRecipes() {
  const client = await pool.connect();
  
  try {
    console.log('Connected to PostgreSQL database');
    
    // Get count before deletion
    const beforeCount = await client.query('SELECT COUNT(*) FROM recipes');
    console.log(`Current recipes in database: ${beforeCount.rows[0].count}`);
    
    // Delete all recipes
    const result = await client.query('DELETE FROM recipes');
    console.log(`✅ Successfully deleted ${result.rowCount} recipes`);
    
    // Verify deletion
    const afterCount = await client.query('SELECT COUNT(*) FROM recipes');
    console.log(`Remaining recipes: ${afterCount.rows[0].count}`);
    
  } catch (error) {
    console.error('Error clearing recipes:', error);
    throw error;
  } finally {
    client.release();
  }
}

// Run the cleanup
clearRecipes()
  .then(() => {
    console.log('Cleanup completed successfully');
    pool.end();
    process.exit(0);
  })
  .catch((error) => {
    console.error('Cleanup failed:', error);
    pool.end();
    process.exit(1);
  });
