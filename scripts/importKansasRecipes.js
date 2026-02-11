const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');
const { Pool } = require('pg');

const csvFilePath = path.join(__dirname, '../excel docs/Recipes Kansas.csv');

// PostgreSQL configuration - update with your credentials
const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER || 'postgres',
  password: '7646',
  database: process.env.DB_NAME || 'gomums',
});

async function importRecipes() {
  const recipes = [];
  
  return new Promise((resolve, reject) => {
    fs.createReadStream(csvFilePath)
      .pipe(csv())
      .on('data', (row) => {
        try {
          const recipe = {
            name: row.name,
            category: row.category,
            difficulty: row.difficulty,
            prep_time: row.prep_time,
            servings: parseInt(row.servings),
            ingredients: JSON.parse(row.ingredients),
            instructions: JSON.parse(row.instructions || '[]'),
            tags: JSON.parse(row.tags),
            featured: row.featured === 'True',
            image: row.image || null,
            calories: row.calories || null,
            protein: row.protein || null,
            carbs: row.carbs || null,
            fat: row.fat || null,
            fiber: row.fiber || null
          };
          recipes.push(recipe);
        } catch (error) {
          console.error(`Error parsing row: ${row.name}`, error);
        }
      })
      .on('end', async () => {
        console.log(`Found ${recipes.length} recipes to import`);
        
        const client = await pool.connect();
        try {
          console.log('Connected to PostgreSQL database');
          
          for (const recipe of recipes) {
            await client.query(
              `INSERT INTO recipes (name, category, difficulty, prep_time, servings, ingredients, instructions, tags, featured, image, calories, protein, carbs, fat, fiber)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)`,
              [
                recipe.name,
                recipe.category,
                recipe.difficulty,
                recipe.prep_time,
                recipe.servings,
                recipe.ingredients,
                recipe.instructions,
                recipe.tags,
                recipe.featured,
                recipe.image,
                recipe.calories,
                recipe.protein,
                recipe.carbs,
                recipe.fat,
                recipe.fiber
              ]
            );
            console.log(`✓ Imported: ${recipe.name}`);
          }
          
          console.log(`\n✅ Successfully imported ${recipes.length} recipes!`);
        } catch (error) {
          console.error('Error inserting recipes:', error);
          reject(error);
        } finally {
          client.release();
        }
        resolve();
      })
      .on('error', (error) => {
        console.error('Error reading CSV file:', error);
        reject(error);
      });
  });
}

// Run the import
importRecipes()
  .then(() => {
    console.log('Import completed successfully');
    pool.end();
    process.exit(0);
  })
  .catch((error) => {
    console.error('Import failed:', error);
    pool.end();
    process.exit(1);
  });
