const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'gomums',
  user: 'postgres',
  password: '7646'
});

// Category-based image URLs from Unsplash
const categoryImages = {
  'Main Course': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800',
  'Dessert': 'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=800',
  'Side Dish': 'https://images.unsplash.com/photo-1505253716362-afaea1d3d1af?w=800',
  'Breakfast': 'https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=800',
  'Soup': 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=800',
  'Appetizer': 'https://images.unsplash.com/photo-1599974177577-f1ba82545d7c?w=800',
  'Beverage': 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=800',
  'Lunch': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800',
  'Salad': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800',
  'Snack': 'https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=800',
  'Condiment': 'https://images.unsplash.com/photo-1596040033229-a0b13fdfd21d?w=800',
  'Bread': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800',
  'default': 'https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=800'
};

// Nutrition estimates by category (reasonable averages)
const categoryNutrition = {
  'Main Course': { calories: 420, protein: '32g', carbs: '38g', fat: '16g', fiber: '4g' },
  'Dessert': { calories: 320, protein: '4g', carbs: '52g', fat: '12g', fiber: '2g' },
  'Side Dish': { calories: 180, protein: '4g', carbs: '28g', fat: '6g', fiber: '3g' },
  'Breakfast': { calories: 380, protein: '18g', carbs: '45g', fat: '14g', fiber: '5g' },
  'Soup': { calories: 220, protein: '12g', carbs: '24g', fat: '8g', fiber: '4g' },
  'Appetizer': { calories: 160, protein: '8g', carbs: '18g', fat: '7g', fiber: '2g' },
  'Beverage': { calories: 120, protein: '2g', carbs: '28g', fat: '0g', fiber: '0g' },
  'Lunch': { calories: 400, protein: '28g', carbs: '42g', fat: '14g', fiber: '5g' },
  'Salad': { calories: 180, protein: '8g', carbs: '22g', fat: '8g', fiber: '6g' },
  'Snack': { calories: 150, protein: '5g', carbs: '20g', fat: '6g', fiber: '2g' },
  'Condiment': { calories: 45, protein: '1g', carbs: '8g', fat: '2g', fiber: '1g' },
  'Bread': { calories: 220, protein: '8g', carbs: '42g', fat: '4g', fiber: '3g' },
  'default': { calories: 280, protein: '15g', carbs: '35g', fat: '10g', fiber: '3g' }
};

function generateDescription(name, category, difficulty) {
  const difficultyText = {
    'easy': 'simple and straightforward',
    'medium': 'moderately challenging',
    'hard': 'requiring attention to detail'
  }[difficulty] || 'easy to prepare';
  
  const categoryDescriptions = {
    'Main Course': `A satisfying ${name.toLowerCase()} that serves as a complete meal. This ${difficultyText} recipe is perfect for lunch or dinner and delivers great flavor with every bite.`,
    'Dessert': `A delightful ${name.toLowerCase()} that\'s perfect for satisfying your sweet tooth. This ${difficultyText} dessert is ideal for special occasions or everyday treats.`,
    'Side Dish': `A delicious ${name.toLowerCase()} that complements any main course beautifully. This ${difficultyText} side dish adds variety and nutrition to your meal.`,
    'Breakfast': `Start your day right with this ${name.toLowerCase()}. This ${difficultyText} breakfast recipe provides energy and nutrition to fuel your morning.`,
    'Soup': `A comforting bowl of ${name.toLowerCase()} that warms you from the inside out. This ${difficultyText} soup is perfect for any season and makes excellent leftovers.`,
    'Appetizer': `Kick off your meal with this tasty ${name.toLowerCase()}. This ${difficultyText} appetizer is sure to impress your guests and whet their appetites.`,
    'Beverage': `A refreshing ${name.toLowerCase()} that\'s perfect for any time of day. This ${difficultyText} drink recipe offers delicious flavor in every sip.`,
    'Lunch': `A perfect midday meal featuring ${name.toLowerCase()}. This ${difficultyText} lunch recipe is both satisfying and nutritious.`,
    'Salad': `A fresh and crisp ${name.toLowerCase()} packed with flavor and nutrition. This ${difficultyText} salad works great as a side or light main course.`,
    'Snack': `A tasty ${name.toLowerCase()} perfect for between meals. This ${difficultyText} snack satisfies cravings without being too heavy.`,
    'Condiment': `Enhance your dishes with this flavorful ${name.toLowerCase()}. This ${difficultyText} condiment adds the perfect finishing touch to your meals.`,
    'Bread': `Freshly made ${name.toLowerCase()} with a wonderful aroma and texture. This ${difficultyText} bread recipe is perfect for sandwiches or enjoying on its own.`
  };
  
  return categoryDescriptions[category] || 
    `A delicious ${name.toLowerCase()} recipe that\'s ${difficultyText} and perfect for home cooks. This dish brings great flavor and satisfaction to your table.`;
}

async function bulkUpdateRecipes() {
  const client = await pool.connect();
  
  try {
    console.log('\n' + '='.repeat(70));
    console.log('Bulk Updating Remaining Recipes');
    console.log('='.repeat(70) + '\n');
    
    // Get all recipes missing data
    const recipes = await client.query(`
      SELECT id, name, category, difficulty, featured
      FROM recipes
      WHERE description IS NULL OR image IS NULL OR calories IS NULL
      ORDER BY category, name
    `);
    
    console.log(`📋 Found ${recipes.rows.length} recipes to update\n`);
    console.log('Starting bulk update...\n');
    
    let updateCount = 0;
    let batchSize = 50;
    
    await client.query('BEGIN');
    
    for (let i = 0; i < recipes.rows.length; i++) {
      const recipe = recipes.rows[i];
      const category = recipe.category || 'Main Course';
      const difficulty = recipe.difficulty || 'medium';
      
      const description = generateDescription(recipe.name, category, difficulty);
      const image = categoryImages[category] || categoryImages['default'];
      const nutrition = categoryNutrition[category] || categoryNutrition['default'];
      
      await client.query(`
        UPDATE recipes
        SET 
          description = $1,
          image = $2,
          calories = $3,
          protein = $4,
          carbs = $5,
          fat = $6,
          fiber = $7,
          updated_at = CURRENT_TIMESTAMP
        WHERE id = $8
      `, [
        description,
        image,
        nutrition.calories,
        nutrition.protein,
        nutrition.carbs,
        nutrition.fat,
        nutrition.fiber,
        recipe.id
      ]);
      
      updateCount++;
      
      // Progress indicator every 50 recipes
      if (updateCount % batchSize === 0) {
        console.log(`✅ Updated ${updateCount}/${recipes.rows.length} recipes...`);
      }
    }
    
    await client.query('COMMIT');
    
    console.log(`\n✅ Successfully updated ${updateCount} recipes!\n`);
    
    // Verify results
    const verification = await client.query(`
      SELECT 
        COUNT(*) as total,
        COUNT(description) as has_description,
        COUNT(image) as has_image,
        COUNT(calories) as has_calories
      FROM recipes
    `);
    
    const stats = verification.rows[0];
    
    console.log('='.repeat(70));
    console.log('📊 Final Database Status:');
    console.log('='.repeat(70));
    console.log(`Total Recipes: ${stats.total}`);
    console.log(`With Description: ${stats.has_description}/${stats.total} (${Math.round(stats.has_description/stats.total*100)}%)`);
    console.log(`With Image: ${stats.has_image}/${stats.total} (${Math.round(stats.has_image/stats.total*100)}%)`);
    console.log(`With Nutrition: ${stats.has_calories}/${stats.total} (${Math.round(stats.has_calories/stats.total*100)}%)`);
    console.log('='.repeat(70));
    
    // Show sample updated recipes
    const samples = await client.query(`
      SELECT name, category, description, calories, protein
      FROM recipes
      WHERE id IN (
        SELECT id FROM recipes 
        WHERE updated_at > NOW() - INTERVAL '1 minute'
        LIMIT 3
      )
    `);
    
    console.log('\n📋 Sample Updated Recipes:');
    console.log('-'.repeat(70));
    samples.rows.forEach((recipe, index) => {
      console.log(`${index + 1}. ${recipe.name} (${recipe.category})`);
      console.log(`   Description: ${recipe.description.substring(0, 80)}...`);
      console.log(`   Nutrition: ${recipe.calories} cal, ${recipe.protein} protein`);
    });
    
    console.log('\n✨ Bulk update completed successfully!\n');
    
  } catch (error) {
    await client.query('ROLLBACK');
    console.error('❌ Error during bulk update:', error.message);
    throw error;
  } finally {
    client.release();
    await pool.end();
  }
}

bulkUpdateRecipes();
