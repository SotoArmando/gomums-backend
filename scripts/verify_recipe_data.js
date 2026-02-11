const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'gomums',
  user: 'postgres',
  password: '7646'
});

async function verifyRecipeData() {
  try {
    console.log('\n' + '='.repeat(70));
    console.log('Verifying Recipe Enhancement');
    console.log('='.repeat(70) + '\n');
    
    const result = await pool.query(`
      SELECT 
        name,
        description,
        image,
        featured,
        prep_time,
        calories,
        protein,
        carbs,
        fat,
        fiber,
        difficulty,
        servings,
        CASE 
          WHEN steps IS NOT NULL AND jsonb_array_length(steps) > 0 
          THEN jsonb_array_length(steps) 
          ELSE 0 
        END as steps_count
      FROM recipes
      WHERE steps IS NOT NULL 
        AND jsonb_array_length(steps) > 0
      ORDER BY featured DESC, name
      LIMIT 3
    `);
    
    console.log(`✅ Found ${result.rows.length} recipes with complete data:\n`);
    
    result.rows.forEach((recipe, index) => {
      console.log(`${index + 1}. ${recipe.name}`);
      console.log(`   Featured: ${recipe.featured ? '⭐ Yes' : 'No'}`);
      console.log(`   Steps: ${recipe.steps_count} steps`);
      console.log(`   Prep Time: ${recipe.prep_time || 'N/A'}`);
      console.log(`   Servings: ${recipe.servings || 'N/A'}`);
      console.log(`   Difficulty: ${recipe.difficulty || 'N/A'}`);
      console.log(`   Image: ${recipe.image ? '✅ Yes' : '❌ No'}`);
      console.log(`   Description: ${recipe.description ? '✅ Yes' : '❌ No'} (${recipe.description ? recipe.description.length : 0} chars)`);
      console.log(`   Nutrition:`);
      console.log(`      • Calories: ${recipe.calories || 'N/A'}`);
      console.log(`      • Protein: ${recipe.protein || 'N/A'}`);
      console.log(`      • Carbs: ${recipe.carbs || 'N/A'}`);
      console.log(`      • Fat: ${recipe.fat || 'N/A'}`);
      console.log(`      • Fiber: ${recipe.fiber || 'N/A'}`);
      console.log('');
    });
    
    // Check completeness
    const completeness = await pool.query(`
      SELECT 
        COUNT(*) as total,
        COUNT(description) as has_description,
        COUNT(image) as has_image,
        COUNT(calories) as has_calories,
        COUNT(protein) as has_protein,
        COUNT(carbs) as has_carbs,
        COUNT(fat) as has_fat,
        COUNT(fiber) as has_fiber,
        COUNT(prep_time) as has_prep_time
      FROM recipes
      WHERE steps IS NOT NULL 
        AND jsonb_array_length(steps) > 0
    `);
    
    const stats = completeness.rows[0];
    console.log('='.repeat(70));
    console.log('📊 Data Completeness (Recipes with Steps):');
    console.log('='.repeat(70));
    console.log(`Total Recipes: ${stats.total}`);
    console.log(`Description: ${stats.has_description}/${stats.total} (${Math.round(stats.has_description/stats.total*100)}%)`);
    console.log(`Image: ${stats.has_image}/${stats.total} (${Math.round(stats.has_image/stats.total*100)}%)`);
    console.log(`Prep Time: ${stats.has_prep_time}/${stats.total} (${Math.round(stats.has_prep_time/stats.total*100)}%)`);
    console.log(`Calories: ${stats.has_calories}/${stats.total} (${Math.round(stats.has_calories/stats.total*100)}%)`);
    console.log(`Protein: ${stats.has_protein}/${stats.total} (${Math.round(stats.has_protein/stats.total*100)}%)`);
    console.log(`Carbs: ${stats.has_carbs}/${stats.total} (${Math.round(stats.has_carbs/stats.total*100)}%)`);
    console.log(`Fat: ${stats.has_fat}/${stats.total} (${Math.round(stats.has_fat/stats.total*100)}%)`);
    console.log(`Fiber: ${stats.has_fiber}/${stats.total} (${Math.round(stats.has_fiber/stats.total*100)}%)`);
    console.log('='.repeat(70));
    
    if (stats.has_description == stats.total && 
        stats.has_image == stats.total && 
        stats.has_calories == stats.total) {
      console.log('\n✨ All recipes have complete data! Ready for API consumption.\n');
    } else {
      console.log('\n⚠️  Some recipes are missing data fields.\n');
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await pool.end();
  }
}

verifyRecipeData();
