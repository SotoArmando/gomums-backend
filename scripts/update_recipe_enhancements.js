const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'gomums',
  user: 'postgres',
  password: '7646'
});

// Enhanced recipe data with descriptions, images, and nutrition info
const recipeEnhancements = {
  'Sancocho Dominicano (Dominican Stew)': {
    description: 'A hearty and traditional Dominican stew made with a variety of meats and root vegetables. This soul-warming dish is perfect for family gatherings and represents the rich culinary heritage of the Dominican Republic. The combination of meats and vegetables creates a deeply flavorful broth that\'s both nutritious and satisfying.',
    image: 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=800',
    featured: true,
    calories: 450,
    protein: '35g',
    carbs: '48g',
    fat: '12g',
    fiber: '8g'
  },
  'La Bandera Dominicana (The Flag)': {
    description: 'The national dish of the Dominican Republic, featuring white rice, red beans, and stewed meat served together on one plate. This iconic meal represents the colors of the Dominican flag and is enjoyed daily by families across the country. It\'s a complete, balanced meal that\'s both delicious and nutritious.',
    image: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=800',
    featured: true,
    calories: 520,
    protein: '32g',
    carbs: '65g',
    fat: '14g',
    fiber: '12g'
  },
  'Moro de Guandules (Rice with Pigeon Peas)': {
    description: 'A flavorful Dominican rice dish cooked with pigeon peas and coconut milk, creating a creamy and aromatic side or main dish. This traditional recipe showcases the African influence in Dominican cuisine and is especially popular during holidays and special occasions. The coconut milk adds richness while the sofrito provides depth of flavor.',
    image: 'https://images.unsplash.com/photo-1516684732162-798a0062be99?w=800',
    featured: false,
    calories: 380,
    protein: '12g',
    carbs: '62g',
    fat: '10g',
    fiber: '8g'
  },
  'Pollo Guisado (Dominican Stewed Chicken)': {
    description: 'Tender chicken pieces simmered in a rich tomato-based sofrito sauce, creating a flavorful and comforting main dish. This is one of the most beloved dishes in Dominican cuisine, served at both everyday meals and special celebrations. The slow-simmering process ensures the chicken absorbs all the wonderful flavors of the aromatic sauce.',
    image: 'https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=800',
    featured: true,
    calories: 420,
    protein: '38g',
    carbs: '18g',
    fat: '22g',
    fiber: '3g'
  },
  'Mangú con Los Tres Golpes': {
    description: 'A classic Dominican breakfast featuring mashed green plantains topped with pickled onions, served with fried salami, cheese, and eggs. This hearty morning meal provides sustained energy throughout the day and is a cherished part of Dominican food culture. The contrast between the creamy mangú and crispy accompaniments creates a perfect balance.',
    image: 'https://images.unsplash.com/photo-1525351484163-7529414344d8?w=800',
    featured: false,
    calories: 620,
    protein: '28g',
    carbs: '58g',
    fat: '32g',
    fiber: '6g'
  },
  'Classic Roasted Chicken': {
    description: 'A perfectly roasted whole chicken with crispy golden skin and juicy meat, accompanied by tender roasted vegetables. This timeless recipe is ideal for family dinners and makes excellent leftovers. The simple seasoning allows the natural flavors of quality chicken to shine through while creating an impressive presentation.',
    image: 'https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=800',
    featured: true,
    calories: 380,
    protein: '42g',
    carbs: '22g',
    fat: '14g',
    fiber: '4g'
  },
  'Creamy Chicken Pasta': {
    description: 'Tender chicken pieces tossed with pasta in a rich, creamy sauce that\'s both comforting and satisfying. This quick and easy weeknight dinner comes together in under 30 minutes but tastes like you spent hours in the kitchen. The creamy sauce clings perfectly to every strand of pasta.',
    image: 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=800',
    featured: false,
    calories: 580,
    protein: '35g',
    carbs: '62g',
    fat: '18g',
    fiber: '3g'
  },
  'Chicken Stir-Fry': {
    description: 'Quick and flavorful stir-fried chicken with vegetables served over steamed rice. This Asian-inspired dish is perfect for busy weeknights when you want something healthy and delicious fast. The high-heat cooking method creates wonderful caramelization and keeps vegetables crisp.',
    image: 'https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=800',
    featured: false,
    calories: 420,
    protein: '32g',
    carbs: '52g',
    fat: '10g',
    fiber: '4g'
  },
  'Honey Garlic Chicken': {
    description: 'Succulent chicken pieces glazed with a sweet and savory honey garlic sauce that caramelizes beautifully. This crowd-pleasing recipe combines the perfect balance of sweet honey and pungent garlic, creating an irresistible flavor combination. The sticky sauce coats every piece of tender chicken.',
    image: 'https://images.unsplash.com/photo-1633964913295-ceb43826e36e?w=800',
    featured: true,
    calories: 440,
    protein: '36g',
    carbs: '42g',
    fat: '12g',
    fiber: '1g'
  },
  'Lemon Herb Chicken': {
    description: 'Bright and fresh pan-seared chicken breasts with a zesty lemon and herb sauce. This light yet flavorful dish is perfect for health-conscious eaters who don\'t want to sacrifice taste. The citrus notes and aromatic herbs create a restaurant-quality meal at home.',
    image: 'https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=800',
    featured: false,
    calories: 320,
    protein: '38g',
    carbs: '8g',
    fat: '14g',
    fiber: '1g'
  }
};

async function updateRecipes() {
  try {
    console.log('\n' + '='.repeat(70));
    console.log('Updating Recipes with Enhanced Data');
    console.log('='.repeat(70) + '\n');
    
    let updatedCount = 0;
    let notFoundCount = 0;
    
    for (const [recipeName, data] of Object.entries(recipeEnhancements)) {
      const result = await pool.query(`
        UPDATE recipes 
        SET 
          description = $1,
          image = $2,
          featured = $3,
          calories = $4,
          protein = $5,
          carbs = $6,
          fat = $7,
          fiber = $8,
          updated_at = CURRENT_TIMESTAMP
        WHERE name = $9
        RETURNING id, name
      `, [
        data.description,
        data.image,
        data.featured,
        data.calories,
        data.protein,
        data.carbs,
        data.fat,
        data.fiber,
        recipeName
      ]);
      
      if (result.rowCount > 0) {
        console.log(`✅ Updated: ${recipeName}`);
        console.log(`   • Description: ${data.description.substring(0, 60)}...`);
        console.log(`   • Image: ${data.image}`);
        console.log(`   • Featured: ${data.featured ? 'Yes' : 'No'}`);
        console.log(`   • Nutrition: ${data.calories} cal, ${data.protein} protein, ${data.carbs} carbs, ${data.fat} fat`);
        console.log('');
        updatedCount++;
      } else {
        console.log(`❌ Not found: ${recipeName}`);
        notFoundCount++;
      }
    }
    
    console.log('='.repeat(70));
    console.log('📊 Update Summary:');
    console.log(`   ✅ Updated: ${updatedCount} recipes`);
    console.log(`   ❌ Not found: ${notFoundCount} recipes`);
    console.log(`   📝 Total processed: ${Object.keys(recipeEnhancements).length} recipes`);
    console.log('='.repeat(70) + '\n');
    
    // Show sample of updated recipe
    if (updatedCount > 0) {
      const sample = await pool.query(`
        SELECT name, description, image, featured, calories, protein, carbs, fat, fiber
        FROM recipes
        WHERE name = $1
      `, ['Sancocho Dominicano (Dominican Stew)']);
      
      if (sample.rows.length > 0) {
        const recipe = sample.rows[0];
        console.log('📋 Sample Updated Recipe:');
        console.log('-'.repeat(70));
        console.log(`Name: ${recipe.name}`);
        console.log(`Description: ${recipe.description}`);
        console.log(`Image: ${recipe.image}`);
        console.log(`Featured: ${recipe.featured}`);
        console.log(`Nutrition: ${recipe.calories} cal | ${recipe.protein} protein | ${recipe.carbs} carbs | ${recipe.fat} fat | ${recipe.fiber} fiber`);
        console.log('-'.repeat(70) + '\n');
      }
    }
    
    console.log('✨ Recipe enhancement completed!\n');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

updateRecipes();
