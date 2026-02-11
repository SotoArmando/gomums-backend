const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'gomums',
  user: 'postgres',
  password: '7646'
});

async function checkRemainingRecipes() {
  try {
    console.log('\n' + '='.repeat(70));
    console.log('Checking Recipes Without Complete Data');
    console.log('='.repeat(70) + '\n');
    
    // Get all recipes missing data
    const result = await pool.query(`
      SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN description IS NULL THEN 1 END) as missing_description,
        COUNT(CASE WHEN image IS NULL THEN 1 END) as missing_image,
        COUNT(CASE WHEN calories IS NULL THEN 1 END) as missing_calories
      FROM recipes
    `);
    
    const stats = result.rows[0];
    
    console.log('📊 Recipe Data Status:');
    console.log('-'.repeat(70));
    console.log(`Total Recipes: ${stats.total}`);
    console.log(`Missing Description: ${stats.missing_description}`);
    console.log(`Missing Image: ${stats.missing_image}`);
    console.log(`Missing Nutrition: ${stats.missing_calories}`);
    console.log('');
    
    // Get sample of recipes without complete data
    const samples = await pool.query(`
      SELECT id, name, category, difficulty, prep_time, servings
      FROM recipes
      WHERE description IS NULL OR image IS NULL OR calories IS NULL
      ORDER BY name
      LIMIT 10
    `);
    
    if (samples.rows.length > 0) {
      console.log('📋 Sample Recipes Needing Updates:');
      console.log('-'.repeat(70));
      samples.rows.forEach((recipe, index) => {
        console.log(`${index + 1}. ${recipe.name}`);
        console.log(`   Category: ${recipe.category || 'N/A'}`);
        console.log(`   Difficulty: ${recipe.difficulty || 'N/A'}`);
      });
      console.log('\n...(and more)\n');
    }
    
    // Get category breakdown
    const categories = await pool.query(`
      SELECT 
        category,
        COUNT(*) as count,
        COUNT(CASE WHEN description IS NULL THEN 1 END) as missing_data
      FROM recipes
      WHERE description IS NULL OR image IS NULL OR calories IS NULL
      GROUP BY category
      ORDER BY count DESC
    `);
    
    if (categories.rows.length > 0) {
      console.log('📂 Recipes by Category (needing updates):');
      console.log('-'.repeat(70));
      categories.rows.forEach(cat => {
        console.log(`${cat.category || 'Uncategorized'}: ${cat.missing_data} recipes`);
      });
    }
    
    console.log('\n' + '='.repeat(70) + '\n');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await pool.end();
  }
}

checkRemainingRecipes();
