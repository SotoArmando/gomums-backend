const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'gomums',
  user: 'postgres',
  password: '7646'
});

async function checkStepRecipesDescription() {
  try {
    console.log('\n' + '='.repeat(70));
    console.log('Checking Recipes with Steps - Description Status');
    console.log('='.repeat(70) + '\n');
    
    const result = await pool.query(`
      SELECT 
        name,
        description,
        image,
        calories,
        protein,
        carbs,
        fat,
        fiber,
        featured,
        jsonb_array_length(steps) as steps_count,
        CASE 
          WHEN description IS NOT NULL AND LENGTH(description) > 0 THEN '✅'
          ELSE '❌'
        END as has_description,
        CASE 
          WHEN description IS NOT NULL THEN LENGTH(description)
          ELSE 0
        END as description_length
      FROM recipes
      WHERE steps IS NOT NULL 
        AND jsonb_array_length(steps) > 0
      ORDER BY name
    `);
    
    console.log(`Found ${result.rows.length} recipes with steps:\n`);
    
    result.rows.forEach((recipe, index) => {
      console.log(`${index + 1}. ${recipe.name}`);
      console.log(`   Description: ${recipe.has_description} ${recipe.description_length > 0 ? `(${recipe.description_length} chars)` : '(MISSING)'}`);
      console.log(`   Image: ${recipe.image ? '✅' : '❌'}`);
      console.log(`   Nutrition: ${recipe.calories ? '✅' : '❌'} (${recipe.calories} cal, ${recipe.protein}, ${recipe.carbs}, ${recipe.fat})`);
      console.log(`   Steps: ${recipe.steps_count} steps`);
      console.log(`   Featured: ${recipe.featured ? '⭐ Yes' : 'No'}`);
      
      if (recipe.description && recipe.description_length > 0) {
        console.log(`   Preview: "${recipe.description.substring(0, 80)}..."`);
      }
      console.log('');
    });
    
    console.log('='.repeat(70));
    const allHaveDescription = result.rows.every(r => r.description && r.description.length > 0);
    if (allHaveDescription) {
      console.log('✨ YES! All 10 recipes with steps have descriptions!');
    } else {
      const missing = result.rows.filter(r => !r.description || r.description.length === 0);
      console.log(`⚠️  ${missing.length} recipe(s) with steps are missing descriptions:`);
      missing.forEach(r => console.log(`   - ${r.name}`));
    }
    console.log('='.repeat(70) + '\n');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await pool.end();
  }
}

checkStepRecipesDescription();
