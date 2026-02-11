const { Pool } = require('pg');

// PostgreSQL configuration
const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER || 'postgres',
  password: '7646',
  database: process.env.DB_NAME || 'gomums',
});

// Recipe steps with phases
const recipeSteps = {
  'Sancocho Dominicano (Dominican Stew)': [
    { order: 1, phase: 'prep', text: 'Season all meats with salt, pepper, oregano, and half of the mashed garlic. Let marinate for 30 minutes.' },
    { order: 2, phase: 'cooking', text: 'In a large pot, bring 12 cups of water to a boil. Add the meats and cook for 30 minutes, skimming any foam.' },
    { order: 3, phase: 'cooking', text: 'Add cassava, plantains, sweet potato, pumpkin, and corn. Cook for 45 minutes until vegetables are tender.' },
    { order: 4, phase: 'cooking', text: 'In a separate pan, sauté onions, garlic, and bell pepper. Add to the pot along with cilantro.' },
    { order: 5, phase: 'cooking', text: 'Simmer for 15 more minutes. Adjust seasoning to taste.' },
    { order: 6, phase: 'serve', text: 'Serve hot in deep bowls with white rice and avocado on the side.' }
  ],
  'La Bandera Dominicana (The Flag)': [
    { order: 1, phase: 'prep', text: 'Cook beans: Boil pre-soaked beans with water until tender, about 30 minutes. Season with salt.' },
    { order: 2, phase: 'prep', text: 'Make sofrito: Sauté diced onions, garlic, bell pepper, tomatoes, and cilantro in oil until fragrant.' },
    { order: 3, phase: 'cooking', text: 'Season chicken with adobo and brown in a pan. Add half the sofrito and simmer for 25 minutes until cooked through.' },
    { order: 4, phase: 'cooking', text: 'Cook rice: Rinse rice, add to pot with water (1:2 ratio), bring to boil, then simmer covered for 20 minutes.' },
    { order: 5, phase: 'cooking', text: 'Finish beans: Add remaining sofrito to cooked beans and simmer for 10 minutes.' },
    { order: 6, phase: 'serve', text: 'Serve by arranging rice, beans, and chicken on a plate with a side salad.' }
  ],
  'Moro de Guandules (Rice with Pigeon Peas)': [
    { order: 1, phase: 'prep', text: 'Drain pigeon peas, reserving the liquid. Rinse rice thoroughly.' },
    { order: 2, phase: 'prep', text: 'Heat oil in a large pot. Sauté diced onions, garlic, pepper, and cilantro until softened.' },
    { order: 3, phase: 'cooking', text: 'Add tomato paste and adobo seasoning, stirring for 2 minutes.' },
    { order: 4, phase: 'cooking', text: 'Add rice and stir to coat with the sofrito. Add pigeon peas and mix well.' },
    { order: 5, phase: 'cooking', text: 'Pour in coconut milk and enough reserved pea liquid to cover rice by 1 inch. Add salt to taste.' },
    { order: 6, phase: 'serve', text: 'Bring to a boil, then reduce heat to low. Cover and cook for 25 minutes until rice is tender. Fluff and serve hot.' }
  ],
  'Pollo Guisado (Dominican Stewed Chicken)': [
    { order: 1, phase: 'prep', text: 'Cut chicken into pieces. Mix adobo, oregano, vinegar, salt, and pepper. Marinate chicken for 20 minutes.' },
    { order: 2, phase: 'prep', text: 'Blend tomatoes, onions, garlic, bell pepper, and cilantro to make a sofrito.' },
    { order: 3, phase: 'cooking', text: 'Heat oil in a large pot. Brown chicken pieces on all sides, about 5 minutes per side.' },
    { order: 4, phase: 'cooking', text: 'Add the sofrito and tomato sauce to the pot. Stir to coat chicken.' },
    { order: 5, phase: 'cooking', text: 'Add 1 cup of water, bring to a boil, then reduce heat. Cover and simmer for 25 minutes until chicken is tender.' },
    { order: 6, phase: 'serve', text: 'Serve hot over white rice with the flavorful sauce spooned on top.' }
  ],
  'Mangú con Los Tres Golpes': [
    { order: 1, phase: 'prep', text: 'Peel and cut plantains into chunks. Boil in salted water for 20 minutes until very soft.' },
    { order: 2, phase: 'prep', text: 'Meanwhile, slice onions thinly. Heat vinegar with 2 tbsp water and pour over onions. Let sit for 10 minutes for pickled onions.' },
    { order: 3, phase: 'cooking', text: 'Fry salami slices in a pan until crispy, about 3 minutes per side. Fry cheese slices until golden.' },
    { order: 4, phase: 'cooking', text: 'Fry eggs sunny-side up or to your preference.' },
    { order: 5, phase: 'cooking', text: 'Drain plantains and mash with butter until smooth and creamy.' },
    { order: 6, phase: 'serve', text: 'Serve mangú in the center of the plate topped with pickled onions, with fried salami, cheese, and egg on the sides.' }
  ],
  'Classic Roasted Chicken': [
    { order: 1, phase: 'prep', text: 'Preheat oven to 425°F. Pat chicken dry and season generously with salt, pepper, and thyme.' },
    { order: 2, phase: 'prep', text: 'Peel and quarter potatoes. Slice onions and mince garlic.' },
    { order: 3, phase: 'prep', text: 'Place chicken in a roasting pan. Arrange potatoes and onions around it. Drizzle everything with olive oil and scatter garlic on top.' },
    { order: 4, phase: 'cooking', text: 'Roast for 45 minutes, then baste chicken with pan juices. Continue roasting for 30-45 more minutes until internal temperature reaches 165°F.' },
    { order: 5, phase: 'cooking', text: 'Let chicken rest for 10 minutes before carving.' },
    { order: 6, phase: 'serve', text: 'Serve sliced chicken with roasted vegetables and pan juices drizzled over the top.' }
  ],
  'Creamy Chicken Pasta': [
    { order: 1, phase: 'prep', text: 'Bring a large pot of salted water to boil. Cook pasta according to package directions until al dente. Reserve 1 cup pasta water before draining.' },
    { order: 2, phase: 'prep', text: 'Cut chicken into bite-sized pieces. Season with salt and pepper.' },
    { order: 3, phase: 'cooking', text: 'Heat 2 tbsp olive oil in a large skillet over medium-high heat. Cook chicken until golden and cooked through, about 6-8 minutes. Remove and set aside.' },
    { order: 4, phase: 'cooking', text: 'In the same skillet, add remaining oil and minced garlic. Sauté for 1 minute until fragrant.' },
    { order: 5, phase: 'cooking', text: 'Add milk and cheese, stirring until melted. Add pasta and chicken, tossing to coat. Add pasta water if needed to thin the sauce.' },
    { order: 6, phase: 'serve', text: 'Garnish with fresh parsley and serve immediately with extra cheese on the side.' }
  ],
  'Chicken Stir-Fry': [
    { order: 1, phase: 'prep', text: 'Cook rice according to package directions and keep warm.' },
    { order: 2, phase: 'prep', text: 'Slice chicken into thin strips. Slice onions and mince garlic.' },
    { order: 3, phase: 'cooking', text: 'Heat oil in a large wok or skillet over high heat until nearly smoking.' },
    { order: 4, phase: 'cooking', text: 'Add chicken and stir-fry for 5-6 minutes until golden and cooked through. Remove and set aside.' },
    { order: 5, phase: 'cooking', text: 'Add onions and garlic to the wok, stir-fry for 2-3 minutes. Return chicken to wok.' },
    { order: 6, phase: 'serve', text: 'Add soy sauce and toss everything together for 1 minute. Serve immediately over rice.' }
  ],
  'Honey Garlic Chicken': [
    { order: 1, phase: 'prep', text: 'Cut chicken into bite-sized pieces and season with salt.' },
    { order: 2, phase: 'prep', text: 'In a small bowl, whisk together honey, minced garlic, and soy sauce.' },
    { order: 3, phase: 'cooking', text: 'Heat 2 tbsp olive oil in a large skillet over medium-high heat.' },
    { order: 4, phase: 'cooking', text: 'Add chicken and cook for 8-10 minutes, stirring occasionally, until browned and cooked through.' },
    { order: 5, phase: 'cooking', text: 'Pour honey garlic sauce over chicken and toss to coat. Cook for 2-3 more minutes until sauce thickens and caramelizes.' },
    { order: 6, phase: 'serve', text: 'Serve hot over rice or with steamed vegetables.' }
  ],
  'Lemon Herb Chicken': [
    { order: 1, phase: 'prep', text: 'Pat chicken dry and season both sides with salt, pepper, and thyme.' },
    { order: 2, phase: 'prep', text: 'In a small bowl, mix lemon juice with minced garlic.' },
    { order: 3, phase: 'cooking', text: 'Heat olive oil in a large skillet over medium-high heat.' },
    { order: 4, phase: 'cooking', text: 'Add chicken and cook for 5-6 minutes per side until golden brown and internal temperature reaches 165°F.' },
    { order: 5, phase: 'cooking', text: 'Pour lemon garlic mixture over chicken in the last 2 minutes of cooking.' },
    { order: 6, phase: 'serve', text: 'Let rest for 5 minutes, then serve with the pan sauce drizzled over the top and fresh lemon wedges.' }
  ]
};

async function updateRecipeSteps() {
  const client = await pool.connect();
  
  try {
    console.log('Connected to PostgreSQL database\n');
    
    let updated = 0;
    let notFound = 0;
    
    for (const [recipeName, steps] of Object.entries(recipeSteps)) {
      try {
        // Check if recipe exists
        const checkResult = await client.query(
          'SELECT id FROM recipes WHERE name = $1',
          [recipeName]
        );
        
        if (checkResult.rows.length === 0) {
          console.log(`⚠️  Recipe not found: ${recipeName}`);
          notFound++;
          continue;
        }
        
        // Update recipe with structured steps
        await client.query(
          'UPDATE recipes SET steps = $1, updated_at = NOW() WHERE name = $2',
          [JSON.stringify(steps), recipeName]
        );
        
        console.log(`✅ Updated: ${recipeName} (${steps.length} steps)`);
        updated++;
        
      } catch (error) {
        console.error(`❌ Error updating ${recipeName}:`, error.message);
      }
    }
    
    console.log(`\n📊 Summary:`);
    console.log(`   Updated: ${updated} recipes`);
    console.log(`   Not found: ${notFound} recipes`);
    console.log(`   Total: ${Object.keys(recipeSteps).length} recipes processed`);
    
  } catch (error) {
    console.error('Error updating recipe steps:', error);
    throw error;
  } finally {
    client.release();
  }
}

// Run the update
updateRecipeSteps()
  .then(() => {
    console.log('\n✨ Update completed successfully');
    pool.end();
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n❌ Update failed:', error);
    pool.end();
    process.exit(1);
  });
