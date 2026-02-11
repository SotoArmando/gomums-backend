const { Pool } = require('pg');

// PostgreSQL configuration
const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER || 'postgres',
  password: '7646',
  database: process.env.DB_NAME || 'gomums',
});

async function checkSchema() {
  const client = await pool.connect();
  
  try {
    console.log('Checking recipes table schema:\n');
    
    const result = await client.query(`
      SELECT column_name, data_type, is_nullable, column_default
      FROM information_schema.columns
      WHERE table_name = 'recipes'
      ORDER BY ordinal_position;
    `);
    
    console.log('Columns in recipes table:');
    console.log('─'.repeat(80));
    result.rows.forEach(row => {
      console.log(`${row.column_name.padEnd(30)} ${row.data_type.padEnd(20)} ${row.is_nullable}`);
    });
    console.log('─'.repeat(80));
    console.log(`\nTotal columns: ${result.rows.length}`);
    
    // Check if steps column exists
    const hasSteps = result.rows.some(row => row.column_name === 'steps');
    const hasInstructions = result.rows.some(row => row.column_name === 'instructions');
    
    console.log(`\n✓ Has 'instructions' column: ${hasInstructions}`);
    console.log(`✓ Has 'steps' column: ${hasSteps}`);
    
  } catch (error) {
    console.error('Error checking schema:', error.message);
    throw error;
  } finally {
    client.release();
  }
}

// Run the check
checkSchema()
  .then(() => {
    pool.end();
    process.exit(0);
  })
  .catch((error) => {
    console.error('Failed:', error);
    pool.end();
    process.exit(1);
  });
