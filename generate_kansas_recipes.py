import csv
import json
import random

# Available ingredients from Kansas.csv with typical amounts used in recipes
ingredients_pool = {
    'Milk': ['1 cup', '2 cups', '1/2 cup', '1 liter'],
    'Fresh White Bread': ['2 slices', '4 slices', '1 loaf', '6 slices'],
    'White Rice': ['1 cup', '2 cups', '1/2 cup', '3 cups'],
    'Eggs': ['2 eggs', '3 eggs', '4 eggs', '1 egg', '6 eggs'],
    'Local Cheese': ['1 cup shredded', '1/2 cup', '8 oz', '4 oz'],
    'Chicken Fillets': ['1 lb', '1.5 lbs', '2 lbs', '8 oz'],
    'Beef Round': ['1 lb', '1.5 lbs', '2 lbs', '12 oz'],
    'Apples': ['2 apples', '3 apples', '1 apple', '4 apples'],
    'Bananas': ['2 bananas', '3 bananas', '1 banana', '4 bananas'],
    'Oranges': ['2 oranges', '3 oranges', '1 orange', '4 oranges'],
    'Tomatoes': ['2 tomatoes', '3 tomatoes', '4 tomatoes', '1 can diced'],
    'Potatoes': ['2 lbs', '4 potatoes', '3 potatoes', '1 lb'],
    'Onions': ['1 onion', '2 onions', '1/2 onion', '1 large onion'],
    'Lettuce': ['1 head', '1/2 head', '2 cups chopped'],
    'Bottled Water': ['2 cups', '1 cup', '3 cups'],
    'Wine': ['1/2 cup', '1 cup', '1/4 cup'],
    'Beer': ['1 bottle', '1 can', '1/2 cup']
}

# Pantry staples to complement recipes
pantry_items = {
    'Olive Oil': ['2 tbsp', '3 tbsp', '1/4 cup', '1 tbsp'],
    'Butter': ['2 tbsp', '3 tbsp', '4 tbsp', '1/4 cup'],
    'Salt': ['1 tsp', '1/2 tsp', '2 tsp', 'to taste'],
    'Black Pepper': ['1/2 tsp', '1 tsp', 'to taste', '1/4 tsp'],
    'Garlic': ['2 cloves', '3 cloves', '4 cloves', '1 clove'],
    'Flour': ['1 cup', '2 cups', '1/2 cup', '1/4 cup'],
    'Sugar': ['1/2 cup', '1 cup', '2 tbsp', '1/4 cup'],
    'Soy Sauce': ['2 tbsp', '3 tbsp', '1 tbsp'],
    'Lemon Juice': ['2 tbsp', '1 tbsp', '3 tbsp'],
    'Parsley': ['2 tbsp chopped', '1/4 cup chopped', '1 tbsp'],
    'Basil': ['1 tbsp', '2 tbsp', '1/4 cup fresh'],
    'Oregano': ['1 tsp', '1/2 tsp', '2 tsp'],
    'Paprika': ['1 tsp', '1/2 tsp', '2 tsp'],
    'Cumin': ['1 tsp', '1/2 tsp', '2 tsp'],
    'Thyme': ['1 tsp', '1/2 tsp'],
    'Bay Leaves': ['2 leaves', '1 leaf'],
    'Honey': ['2 tbsp', '1 tbsp', '3 tbsp'],
    'Vinegar': ['2 tbsp', '1 tbsp', '3 tbsp'],
    'Mustard': ['1 tbsp', '2 tbsp', '1 tsp'],
    'Ketchup': ['2 tbsp', '3 tbsp', '1/4 cup']
}

# 100 recipe ideas
recipes = [
    # Chicken Recipes (20)
    {'name': 'Classic Roasted Chicken', 'category': 'Main Course', 'difficulty': 'medium', 'prep_time': '1 hour 30 minutes', 'servings': 6, 'main': ['Chicken Fillets'], 'secondary': ['Onions', 'Potatoes', 'Garlic', 'Olive Oil', 'Thyme', 'Salt', 'Black Pepper'], 'tags': ['roasted', 'chicken', 'dinner']},
    {'name': 'Creamy Chicken Pasta', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '30 minutes', 'servings': 4, 'main': ['Chicken Fillets'], 'secondary': ['Milk', 'Local Cheese', 'Garlic', 'Olive Oil', 'Parsley', 'Salt', 'Black Pepper'], 'tags': ['pasta', 'chicken', 'creamy']},
    {'name': 'Chicken Stir-Fry', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '25 minutes', 'servings': 4, 'main': ['Chicken Fillets'], 'secondary': ['White Rice', 'Onions', 'Garlic', 'Soy Sauce', 'Olive Oil'], 'tags': ['stir-fry', 'chicken', 'asian']},
    {'name': 'Honey Garlic Chicken', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '35 minutes', 'servings': 4, 'main': ['Chicken Fillets'], 'secondary': ['Honey', 'Garlic', 'Soy Sauce', 'Olive Oil', 'Salt'], 'tags': ['chicken', 'sweet', 'garlic']},
    {'name': 'Lemon Herb Chicken', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '40 minutes', 'servings': 4, 'main': ['Chicken Fillets'], 'secondary': ['Lemon Juice', 'Garlic', 'Thyme', 'Olive Oil', 'Salt', 'Black Pepper'], 'tags': ['chicken', 'lemon', 'herbs']},
    {'name': 'Chicken and Rice Casserole', 'category': 'Main Course', 'difficulty': 'medium', 'prep_time': '1 hour', 'servings': 6, 'main': ['Chicken Fillets', 'White Rice'], 'secondary': ['Onions', 'Milk', 'Local Cheese', 'Butter', 'Salt', 'Black Pepper'], 'tags': ['casserole', 'chicken', 'rice']},
    {'name': 'BBQ Chicken', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '45 minutes', 'servings': 4, 'main': ['Chicken Fillets'], 'secondary': ['Ketchup', 'Honey', 'Garlic', 'Paprika', 'Salt'], 'tags': ['bbq', 'chicken', 'grilled']},
    {'name': 'Chicken Soup', 'category': 'Soup', 'difficulty': 'easy', 'prep_time': '45 minutes', 'servings': 6, 'main': ['Chicken Fillets'], 'secondary': ['Onions', 'Potatoes', 'Bottled Water', 'Garlic', 'Parsley', 'Salt', 'Black Pepper'], 'tags': ['soup', 'chicken', 'comfort food']},
    {'name': 'Creamy Chicken and Mushroom', 'category': 'Main Course', 'difficulty': 'medium', 'prep_time': '35 minutes', 'servings': 4, 'main': ['Chicken Fillets'], 'secondary': ['Milk', 'Onions', 'Garlic', 'Butter', 'Flour', 'Salt', 'Black Pepper'], 'tags': ['chicken', 'creamy', 'mushroom']},
    {'name': 'Chicken Lettuce Wraps', 'category': 'Appetizer', 'difficulty': 'easy', 'prep_time': '20 minutes', 'servings': 4, 'main': ['Chicken Fillets', 'Lettuce'], 'secondary': ['Onions', 'Garlic', 'Soy Sauce', 'Olive Oil'], 'tags': ['wraps', 'chicken', 'lettuce', 'healthy']},
    {'name': 'Baked Chicken Thighs', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '50 minutes', 'servings': 4, 'main': ['Chicken Fillets'], 'secondary': ['Garlic', 'Paprika', 'Olive Oil', 'Salt', 'Black Pepper'], 'tags': ['baked', 'chicken', 'easy']},
    {'name': 'Chicken Parmesan', 'category': 'Main Course', 'difficulty': 'medium', 'prep_time': '45 minutes', 'servings': 4, 'main': ['Chicken Fillets'], 'secondary': ['Eggs', 'Flour', 'Local Cheese', 'Tomatoes', 'Basil', 'Olive Oil', 'Salt'], 'tags': ['chicken', 'parmesan', 'italian']},
    {'name': 'Chicken Rice Bowl', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '30 minutes', 'servings': 4, 'main': ['Chicken Fillets', 'White Rice'], 'secondary': ['Onions', 'Soy Sauce', 'Garlic', 'Olive Oil', 'Eggs'], 'tags': ['bowl', 'chicken', 'rice']},
    {'name': 'Orange Glazed Chicken', 'category': 'Main Course', 'difficulty': 'medium', 'prep_time': '40 minutes', 'servings': 4, 'main': ['Chicken Fillets', 'Oranges'], 'secondary': ['Honey', 'Garlic', 'Soy Sauce', 'Olive Oil'], 'tags': ['chicken', 'orange', 'glazed']},
    {'name': 'Chicken Quesadilla', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '25 minutes', 'servings': 4, 'main': ['Chicken Fillets'], 'secondary': ['Local Cheese', 'Onions', 'Butter'], 'tags': ['quesadilla', 'chicken', 'mexican']},
    {'name': 'Teriyaki Chicken', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '30 minutes', 'servings': 4, 'main': ['Chicken Fillets'], 'secondary': ['Soy Sauce', 'Honey', 'Garlic', 'White Rice'], 'tags': ['teriyaki', 'chicken', 'asian']},
    {'name': 'Chicken Salad', 'category': 'Salad', 'difficulty': 'easy', 'prep_time': '20 minutes', 'servings': 4, 'main': ['Chicken Fillets', 'Lettuce'], 'secondary': ['Tomatoes', 'Onions', 'Olive Oil', 'Lemon Juice', 'Salt', 'Black Pepper'], 'tags': ['salad', 'chicken', 'healthy']},
    {'name': 'Cheesy Chicken Bake', 'category': 'Main Course', 'difficulty': 'medium', 'prep_time': '50 minutes', 'servings': 6, 'main': ['Chicken Fillets'], 'secondary': ['Local Cheese', 'Milk', 'Butter', 'Flour', 'Garlic', 'Salt'], 'tags': ['baked', 'chicken', 'cheesy']},
    {'name': 'Chicken Fried Rice', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '25 minutes', 'servings': 4, 'main': ['Chicken Fillets', 'White Rice'], 'secondary': ['Eggs', 'Onions', 'Soy Sauce', 'Garlic', 'Olive Oil'], 'tags': ['fried rice', 'chicken', 'asian']},
    {'name': 'Apple Chicken', 'category': 'Main Course', 'difficulty': 'medium', 'prep_time': '45 minutes', 'servings': 4, 'main': ['Chicken Fillets', 'Apples'], 'secondary': ['Onions', 'Butter', 'Thyme', 'Salt', 'Black Pepper'], 'tags': ['chicken', 'apple', 'sweet-savory']},
    
    # Beef Recipes (15)
    {'name': 'Classic Beef Stew', 'category': 'Main Course', 'difficulty': 'medium', 'prep_time': '2 hours', 'servings': 6, 'main': ['Beef Round'], 'secondary': ['Potatoes', 'Onions', 'Bottled Water', 'Garlic', 'Thyme', 'Bay Leaves', 'Olive Oil', 'Salt', 'Black Pepper'], 'tags': ['stew', 'beef', 'comfort food']},
    {'name': 'Beef Stir-Fry', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '30 minutes', 'servings': 4, 'main': ['Beef Round'], 'secondary': ['White Rice', 'Onions', 'Garlic', 'Soy Sauce', 'Olive Oil'], 'tags': ['stir-fry', 'beef', 'asian']},
    {'name': 'Beef and Potato Casserole', 'category': 'Main Course', 'difficulty': 'medium', 'prep_time': '1 hour 15 minutes', 'servings': 6, 'main': ['Beef Round', 'Potatoes'], 'secondary': ['Onions', 'Local Cheese', 'Milk', 'Butter', 'Salt', 'Black Pepper'], 'tags': ['casserole', 'beef', 'potato']},
    {'name': 'Beef Tacos', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '30 minutes', 'servings': 4, 'main': ['Beef Round'], 'secondary': ['Lettuce', 'Tomatoes', 'Onions', 'Local Cheese', 'Cumin', 'Paprika', 'Salt'], 'tags': ['tacos', 'beef', 'mexican']},
    {'name': 'Garlic Beef with Rice', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '35 minutes', 'servings': 4, 'main': ['Beef Round', 'White Rice'], 'secondary': ['Garlic', 'Onions', 'Soy Sauce', 'Olive Oil', 'Black Pepper'], 'tags': ['beef', 'rice', 'garlic']},
    {'name': 'Beef and Onion Skillet', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '25 minutes', 'servings': 4, 'main': ['Beef Round'], 'secondary': ['Onions', 'Garlic', 'Butter', 'Salt', 'Black Pepper'], 'tags': ['beef', 'onion', 'skillet']},
    {'name': 'Beer Braised Beef', 'category': 'Main Course', 'difficulty': 'medium', 'prep_time': '2 hours', 'servings': 6, 'main': ['Beef Round', 'Beer'], 'secondary': ['Onions', 'Garlic', 'Bay Leaves', 'Thyme', 'Olive Oil', 'Salt', 'Black Pepper'], 'tags': ['braised', 'beef', 'beer']},
    {'name': 'Beef Rice Bowl', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '30 minutes', 'servings': 4, 'main': ['Beef Round', 'White Rice'], 'secondary': ['Eggs', 'Onions', 'Soy Sauce', 'Garlic'], 'tags': ['bowl', 'beef', 'rice']},
    {'name': 'Beef Lettuce Wraps', 'category': 'Appetizer', 'difficulty': 'easy', 'prep_time': '20 minutes', 'servings': 4, 'main': ['Beef Round', 'Lettuce'], 'secondary': ['Onions', 'Garlic', 'Soy Sauce', 'Olive Oil'], 'tags': ['wraps', 'beef', 'healthy']},
    {'name': 'Cheesy Beef Bake', 'category': 'Main Course', 'difficulty': 'medium', 'prep_time': '50 minutes', 'servings': 6, 'main': ['Beef Round'], 'secondary': ['Local Cheese', 'Onions', 'Tomatoes', 'Garlic', 'Oregano', 'Salt'], 'tags': ['baked', 'beef', 'cheesy']},
    {'name': 'Beef Soup', 'category': 'Soup', 'difficulty': 'medium', 'prep_time': '1 hour 30 minutes', 'servings': 6, 'main': ['Beef Round'], 'secondary': ['Potatoes', 'Onions', 'Bottled Water', 'Garlic', 'Bay Leaves', 'Salt', 'Black Pepper'], 'tags': ['soup', 'beef', 'hearty']},
    {'name': 'Simple Beef Roast', 'category': 'Main Course', 'difficulty': 'medium', 'prep_time': '2 hours', 'servings': 8, 'main': ['Beef Round'], 'secondary': ['Potatoes', 'Onions', 'Garlic', 'Thyme', 'Olive Oil', 'Salt', 'Black Pepper'], 'tags': ['roast', 'beef', 'dinner']},
    {'name': 'Beef and Egg Breakfast Bowl', 'category': 'Breakfast', 'difficulty': 'easy', 'prep_time': '20 minutes', 'servings': 2, 'main': ['Beef Round', 'Eggs'], 'secondary': ['Onions', 'Butter', 'Salt', 'Black Pepper'], 'tags': ['breakfast', 'beef', 'eggs']},
    {'name': 'Mustard Beef', 'category': 'Main Course', 'difficulty': 'medium', 'prep_time': '40 minutes', 'servings': 4, 'main': ['Beef Round'], 'secondary': ['Mustard', 'Honey', 'Garlic', 'Olive Oil', 'Salt'], 'tags': ['beef', 'mustard', 'tangy']},
    {'name': 'Beef and Tomato Pasta', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '35 minutes', 'servings': 4, 'main': ['Beef Round'], 'secondary': ['Tomatoes', 'Onions', 'Garlic', 'Basil', 'Olive Oil', 'Salt'], 'tags': ['pasta', 'beef', 'tomato']},
    
    # Rice & Vegetable Based (15)
    {'name': 'Classic Fried Rice', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '20 minutes', 'servings': 4, 'main': ['White Rice', 'Eggs'], 'secondary': ['Onions', 'Garlic', 'Soy Sauce', 'Olive Oil'], 'tags': ['fried rice', 'vegetarian', 'asian']},
    {'name': 'Cheese Rice Casserole', 'category': 'Side Dish', 'difficulty': 'easy', 'prep_time': '40 minutes', 'servings': 6, 'main': ['White Rice'], 'secondary': ['Local Cheese', 'Milk', 'Butter', 'Onions', 'Salt'], 'tags': ['casserole', 'rice', 'cheesy']},
    {'name': 'Rice and Beans', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '45 minutes', 'servings': 6, 'main': ['White Rice'], 'secondary': ['Onions', 'Garlic', 'Cumin', 'Olive Oil', 'Salt'], 'tags': ['rice', 'beans', 'vegetarian']},
    {'name': 'Tomato Rice', 'category': 'Side Dish', 'difficulty': 'easy', 'prep_time': '30 minutes', 'servings': 4, 'main': ['White Rice', 'Tomatoes'], 'secondary': ['Onions', 'Garlic', 'Olive Oil', 'Salt'], 'tags': ['rice', 'tomato', 'side dish']},
    {'name': 'Creamy Rice Pudding', 'category': 'Dessert', 'difficulty': 'easy', 'prep_time': '45 minutes', 'servings': 6, 'main': ['White Rice', 'Milk'], 'secondary': ['Sugar', 'Butter', 'Salt'], 'tags': ['dessert', 'rice', 'pudding']},
    {'name': 'Potato Soup', 'category': 'Soup', 'difficulty': 'easy', 'prep_time': '35 minutes', 'servings': 6, 'main': ['Potatoes'], 'secondary': ['Onions', 'Milk', 'Butter', 'Garlic', 'Salt', 'Black Pepper'], 'tags': ['soup', 'potato', 'creamy']},
    {'name': 'Roasted Potatoes', 'category': 'Side Dish', 'difficulty': 'easy', 'prep_time': '40 minutes', 'servings': 4, 'main': ['Potatoes'], 'secondary': ['Garlic', 'Olive Oil', 'Thyme', 'Salt', 'Black Pepper'], 'tags': ['roasted', 'potato', 'side dish']},
    {'name': 'Mashed Potatoes', 'category': 'Side Dish', 'difficulty': 'easy', 'prep_time': '25 minutes', 'servings': 6, 'main': ['Potatoes'], 'secondary': ['Milk', 'Butter', 'Salt', 'Black Pepper'], 'tags': ['mashed', 'potato', 'side dish']},
    {'name': 'Potato Salad', 'category': 'Salad', 'difficulty': 'easy', 'prep_time': '30 minutes', 'servings': 6, 'main': ['Potatoes', 'Eggs'], 'secondary': ['Onions', 'Olive Oil', 'Vinegar', 'Mustard', 'Salt'], 'tags': ['salad', 'potato', 'picnic']},
    {'name': 'Cheesy Potato Bake', 'category': 'Side Dish', 'difficulty': 'medium', 'prep_time': '1 hour', 'servings': 8, 'main': ['Potatoes', 'Local Cheese'], 'secondary': ['Milk', 'Butter', 'Garlic', 'Salt', 'Black Pepper'], 'tags': ['baked', 'potato', 'cheesy']},
    {'name': 'Garden Salad', 'category': 'Salad', 'difficulty': 'easy', 'prep_time': '15 minutes', 'servings': 4, 'main': ['Lettuce', 'Tomatoes'], 'secondary': ['Onions', 'Olive Oil', 'Lemon Juice', 'Salt', 'Black Pepper'], 'tags': ['salad', 'fresh', 'healthy']},
    {'name': 'Tomato Soup', 'category': 'Soup', 'difficulty': 'easy', 'prep_time': '30 minutes', 'servings': 4, 'main': ['Tomatoes'], 'secondary': ['Onions', 'Garlic', 'Basil', 'Olive Oil', 'Salt', 'Black Pepper'], 'tags': ['soup', 'tomato', 'comfort food']},
    {'name': 'Stuffed Tomatoes', 'category': 'Main Course', 'difficulty': 'medium', 'prep_time': '45 minutes', 'servings': 4, 'main': ['Tomatoes', 'White Rice'], 'secondary': ['Onions', 'Local Cheese', 'Garlic', 'Basil', 'Olive Oil', 'Salt'], 'tags': ['stuffed', 'tomato', 'baked']},
    {'name': 'Onion Soup', 'category': 'Soup', 'difficulty': 'medium', 'prep_time': '50 minutes', 'servings': 4, 'main': ['Onions'], 'secondary': ['Fresh White Bread', 'Local Cheese', 'Butter', 'Bottled Water', 'Salt', 'Black Pepper'], 'tags': ['soup', 'onion', 'french']},
    {'name': 'Rice Pilaf', 'category': 'Side Dish', 'difficulty': 'easy', 'prep_time': '30 minutes', 'servings': 4, 'main': ['White Rice'], 'secondary': ['Onions', 'Garlic', 'Butter', 'Parsley', 'Salt'], 'tags': ['rice', 'pilaf', 'side dish']},
    
    # Breakfast & Egg Dishes (12)
    {'name': 'Classic Scrambled Eggs', 'category': 'Breakfast', 'difficulty': 'easy', 'prep_time': '10 minutes', 'servings': 2, 'main': ['Eggs'], 'secondary': ['Milk', 'Butter', 'Salt', 'Black Pepper'], 'tags': ['breakfast', 'eggs', 'quick']},
    {'name': 'French Toast', 'category': 'Breakfast', 'difficulty': 'easy', 'prep_time': '15 minutes', 'servings': 4, 'main': ['Fresh White Bread', 'Eggs'], 'secondary': ['Milk', 'Sugar', 'Butter'], 'tags': ['breakfast', 'french toast', 'sweet']},
    {'name': 'Cheese Omelette', 'category': 'Breakfast', 'difficulty': 'easy', 'prep_time': '15 minutes', 'servings': 2, 'main': ['Eggs', 'Local Cheese'], 'secondary': ['Butter', 'Salt', 'Black Pepper'], 'tags': ['breakfast', 'omelette', 'cheese']},
    {'name': 'Egg Salad Sandwich', 'category': 'Lunch', 'difficulty': 'easy', 'prep_time': '15 minutes', 'servings': 2, 'main': ['Eggs', 'Fresh White Bread'], 'secondary': ['Onions', 'Lettuce', 'Salt', 'Black Pepper'], 'tags': ['sandwich', 'eggs', 'lunch']},
    {'name': 'Baked Eggs', 'category': 'Breakfast', 'difficulty': 'easy', 'prep_time': '20 minutes', 'servings': 4, 'main': ['Eggs'], 'secondary': ['Tomatoes', 'Local Cheese', 'Garlic', 'Basil', 'Olive Oil', 'Salt'], 'tags': ['breakfast', 'eggs', 'baked']},
    {'name': 'Egg Fried Rice', 'category': 'Main Course', 'difficulty': 'easy', 'prep_time': '20 minutes', 'servings': 4, 'main': ['Eggs', 'White Rice'], 'secondary': ['Onions', 'Garlic', 'Soy Sauce', 'Olive Oil'], 'tags': ['fried rice', 'eggs', 'asian']},
    {'name': 'Veggie Omelette', 'category': 'Breakfast', 'difficulty': 'easy', 'prep_time': '20 minutes', 'servings': 2, 'main': ['Eggs'], 'secondary': ['Tomatoes', 'Onions', 'Local Cheese', 'Butter', 'Salt', 'Black Pepper'], 'tags': ['breakfast', 'omelette', 'vegetables']},
    {'name': 'Bread Pudding', 'category': 'Dessert', 'difficulty': 'medium', 'prep_time': '1 hour', 'servings': 8, 'main': ['Fresh White Bread', 'Eggs'], 'secondary': ['Milk', 'Sugar', 'Butter'], 'tags': ['dessert', 'bread', 'pudding']},
    {'name': 'Egg Drop Soup', 'category': 'Soup', 'difficulty': 'easy', 'prep_time': '15 minutes', 'servings': 4, 'main': ['Eggs'], 'secondary': ['Bottled Water', 'Garlic', 'Onions', 'Soy Sauce', 'Salt'], 'tags': ['soup', 'eggs', 'asian']},
    {'name': 'Cheese Toast', 'category': 'Breakfast', 'difficulty': 'easy', 'prep_time': '10 minutes', 'servings': 2, 'main': ['Fresh White Bread', 'Local Cheese'], 'secondary': ['Butter', 'Garlic'], 'tags': ['breakfast', 'toast', 'cheese']},
    {'name': 'Eggs Benedict Style', 'category': 'Breakfast', 'difficulty': 'medium', 'prep_time': '25 minutes', 'servings': 2, 'main': ['Eggs', 'Fresh White Bread'], 'secondary': ['Butter', 'Lemon Juice', 'Salt', 'Black Pepper'], 'tags': ['breakfast', 'eggs', 'fancy']},
    {'name': 'Simple Egg Sandwich', 'category': 'Breakfast', 'difficulty': 'easy', 'prep_time': '10 minutes', 'servings': 1, 'main': ['Eggs', 'Fresh White Bread'], 'secondary': ['Butter', 'Salt', 'Black Pepper'], 'tags': ['breakfast', 'sandwich', 'quick']},
    
    # Desserts & Sweet Dishes (10)
    {'name': 'Banana Bread', 'category': 'Dessert', 'difficulty': 'medium', 'prep_time': '1 hour 15 minutes', 'servings': 10, 'main': ['Bananas'], 'secondary': ['Flour', 'Sugar', 'Eggs', 'Butter', 'Milk'], 'tags': ['dessert', 'banana', 'bread']},
    {'name': 'Apple Crisp', 'category': 'Dessert', 'difficulty': 'easy', 'prep_time': '45 minutes', 'servings': 6, 'main': ['Apples'], 'secondary': ['Sugar', 'Flour', 'Butter'], 'tags': ['dessert', 'apple', 'baked']},
    {'name': 'Baked Apples', 'category': 'Dessert', 'difficulty': 'easy', 'prep_time': '40 minutes', 'servings': 4, 'main': ['Apples'], 'secondary': ['Sugar', 'Butter'], 'tags': ['dessert', 'apple', 'simple']},
    {'name': 'Banana Pancakes', 'category': 'Breakfast', 'difficulty': 'easy', 'prep_time': '20 minutes', 'servings': 4, 'main': ['Bananas', 'Eggs'], 'secondary': ['Flour', 'Milk', 'Sugar', 'Butter'], 'tags': ['breakfast', 'pancakes', 'banana']},
    {'name': 'Caramelized Bananas', 'category': 'Dessert', 'difficulty': 'easy', 'prep_time': '15 minutes', 'servings': 4, 'main': ['Bananas'], 'secondary': ['Sugar', 'Butter'], 'tags': ['dessert', 'banana', 'caramel']},
    {'name': 'Orange Marmalade', 'category': 'Condiment', 'difficulty': 'medium', 'prep_time': '1 hour 30 minutes', 'servings': 16, 'main': ['Oranges'], 'secondary': ['Sugar'], 'tags': ['marmalade', 'orange', 'preserve']},
    {'name': 'Fruit Salad', 'category': 'Dessert', 'difficulty': 'easy', 'prep_time': '15 minutes', 'servings': 6, 'main': ['Apples', 'Bananas', 'Oranges'], 'secondary': ['Honey', 'Lemon Juice'], 'tags': ['dessert', 'fruit', 'healthy']},
    {'name': 'Baked Custard', 'category': 'Dessert', 'difficulty': 'medium', 'prep_time': '50 minutes', 'servings': 6, 'main': ['Eggs', 'Milk'], 'secondary': ['Sugar'], 'tags': ['dessert', 'custard', 'baked']},
    {'name': 'Simple Cheese Cake', 'category': 'Dessert', 'difficulty': 'hard', 'prep_time': '2 hours', 'servings': 12, 'main': ['Local Cheese', 'Eggs'], 'secondary': ['Sugar', 'Flour', 'Butter', 'Milk'], 'tags': ['dessert', 'cheesecake', 'baked']},
    {'name': 'Milk Toast', 'category': 'Dessert', 'difficulty': 'easy', 'prep_time': '10 minutes', 'servings': 2, 'main': ['Fresh White Bread', 'Milk'], 'secondary': ['Sugar', 'Butter'], 'tags': ['dessert', 'toast', 'comfort food']},
    
    # Sandwiches & Light Meals (10)
    {'name': 'Grilled Cheese Sandwich', 'category': 'Lunch', 'difficulty': 'easy', 'prep_time': '10 minutes', 'servings': 1, 'main': ['Fresh White Bread', 'Local Cheese'], 'secondary': ['Butter'], 'tags': ['sandwich', 'cheese', 'lunch']},
    {'name': 'Tomato Cheese Toast', 'category': 'Lunch', 'difficulty': 'easy', 'prep_time': '15 minutes', 'servings': 2, 'main': ['Fresh White Bread', 'Tomatoes', 'Local Cheese'], 'secondary': ['Butter', 'Basil', 'Salt'], 'tags': ['toast', 'tomato', 'cheese']},
    {'name': 'Egg and Cheese Sandwich', 'category': 'Breakfast', 'difficulty': 'easy', 'prep_time': '15 minutes', 'servings': 1, 'main': ['Eggs', 'Fresh White Bread', 'Local Cheese'], 'secondary': ['Butter', 'Salt'], 'tags': ['sandwich', 'breakfast', 'eggs']},
    {'name': 'Chicken Salad Sandwich', 'category': 'Lunch', 'difficulty': 'easy', 'prep_time': '20 minutes', 'servings': 2, 'main': ['Chicken Fillets', 'Fresh White Bread'], 'secondary': ['Lettuce', 'Onions', 'Salt', 'Black Pepper'], 'tags': ['sandwich', 'chicken', 'lunch']},
    {'name': 'BLT Sandwich', 'category': 'Lunch', 'difficulty': 'easy', 'prep_time': '15 minutes', 'servings': 2, 'main': ['Fresh White Bread', 'Lettuce', 'Tomatoes'], 'secondary': ['Butter', 'Salt', 'Black Pepper'], 'tags': ['sandwich', 'classic', 'lunch']},
    {'name': 'Cheese and Onion Sandwich', 'category': 'Lunch', 'difficulty': 'easy', 'prep_time': '10 minutes', 'servings': 1, 'main': ['Fresh White Bread', 'Local Cheese'], 'secondary': ['Onions', 'Butter'], 'tags': ['sandwich', 'cheese', 'onion']},
    {'name': 'Open-Faced Cheese Melt', 'category': 'Lunch', 'difficulty': 'easy', 'prep_time': '12 minutes', 'servings': 2, 'main': ['Fresh White Bread', 'Local Cheese'], 'secondary': ['Tomatoes', 'Garlic', 'Olive Oil'], 'tags': ['open-faced', 'cheese', 'lunch']},
    {'name': 'Chicken Cheese Melt', 'category': 'Lunch', 'difficulty': 'easy', 'prep_time': '20 minutes', 'servings': 2, 'main': ['Chicken Fillets', 'Fresh White Bread', 'Local Cheese'], 'secondary': ['Butter', 'Garlic'], 'tags': ['sandwich', 'chicken', 'cheese']},
    {'name': 'Beef and Cheese Sandwich', 'category': 'Lunch', 'difficulty': 'easy', 'prep_time': '20 minutes', 'servings': 2, 'main': ['Beef Round', 'Fresh White Bread', 'Local Cheese'], 'secondary': ['Onions', 'Mustard'], 'tags': ['sandwich', 'beef', 'cheese']},
    {'name': 'Tomato and Egg Sandwich', 'category': 'Breakfast', 'difficulty': 'easy', 'prep_time': '15 minutes', 'servings': 1, 'main': ['Eggs', 'Fresh White Bread', 'Tomatoes'], 'secondary': ['Butter', 'Salt', 'Black Pepper'], 'tags': ['sandwich', 'breakfast', 'simple']},
    
    # Beverages & Special Dishes (18)
    {'name': 'Banana Smoothie', 'category': 'Beverage', 'difficulty': 'easy', 'prep_time': '5 minutes', 'servings': 2, 'main': ['Bananas', 'Milk'], 'secondary': ['Sugar', 'Honey'], 'tags': ['smoothie', 'banana', 'drink']},
    {'name': 'Orange Juice', 'category': 'Beverage', 'difficulty': 'easy', 'prep_time': '5 minutes', 'servings': 2, 'main': ['Oranges'], 'secondary': ['Sugar'], 'tags': ['juice', 'orange', 'fresh']},
    {'name': 'Apple Cider', 'category': 'Beverage', 'difficulty': 'medium', 'prep_time': '1 hour', 'servings': 8, 'main': ['Apples'], 'secondary': ['Sugar'], 'tags': ['cider', 'apple', 'drink']},
    {'name': 'Hot Milk with Honey', 'category': 'Beverage', 'difficulty': 'easy', 'prep_time': '5 minutes', 'servings': 1, 'main': ['Milk'], 'secondary': ['Honey'], 'tags': ['milk', 'honey', 'warm']},
    {'name': 'Garlic Bread', 'category': 'Side Dish', 'difficulty': 'easy', 'prep_time': '15 minutes', 'servings': 4, 'main': ['Fresh White Bread'], 'secondary': ['Garlic', 'Butter', 'Parsley'], 'tags': ['bread', 'garlic', 'side dish']},
    {'name': 'Wine Poached Pears', 'category': 'Dessert', 'difficulty': 'medium', 'prep_time': '45 minutes', 'servings': 4, 'main': ['Wine'], 'secondary': ['Sugar'], 'tags': ['dessert', 'wine', 'elegant']},
    {'name': 'Beer Battered Onion Rings', 'category': 'Appetizer', 'difficulty': 'medium', 'prep_time': '30 minutes', 'servings': 4, 'main': ['Onions', 'Beer'], 'secondary': ['Flour', 'Eggs', 'Salt', 'Black Pepper'], 'tags': ['appetizer', 'fried', 'onion rings']},
    {'name': 'Cheese Fondue', 'category': 'Appetizer', 'difficulty': 'medium', 'prep_time': '25 minutes', 'servings': 4, 'main': ['Local Cheese', 'Wine'], 'secondary': ['Garlic', 'Fresh White Bread'], 'tags': ['fondue', 'cheese', 'party']},
    {'name': 'Potato Pancakes', 'category': 'Side Dish', 'difficulty': 'medium', 'prep_time': '30 minutes', 'servings': 4, 'main': ['Potatoes', 'Eggs'], 'secondary': ['Onions', 'Flour', 'Salt', 'Black Pepper'], 'tags': ['pancakes', 'potato', 'fried']},
    {'name': 'Apple Butter', 'category': 'Condiment', 'difficulty': 'medium', 'prep_time': '2 hours', 'servings': 20, 'main': ['Apples'], 'secondary': ['Sugar'], 'tags': ['spread', 'apple', 'preserve']},
    {'name': 'Tomato Bruschetta', 'category': 'Appetizer', 'difficulty': 'easy', 'prep_time': '15 minutes', 'servings': 4, 'main': ['Fresh White Bread', 'Tomatoes'], 'secondary': ['Garlic', 'Basil', 'Olive Oil', 'Salt'], 'tags': ['bruschetta', 'italian', 'appetizer']},
    {'name': 'Banana Foster', 'category': 'Dessert', 'difficulty': 'medium', 'prep_time': '20 minutes', 'servings': 4, 'main': ['Bananas'], 'secondary': ['Sugar', 'Butter'], 'tags': ['dessert', 'banana', 'caramel']},
    {'name': 'Orange Chicken', 'category': 'Main Course', 'difficulty': 'medium', 'prep_time': '40 minutes', 'servings': 4, 'main': ['Chicken Fillets', 'Oranges'], 'secondary': ['Soy Sauce', 'Honey', 'Garlic', 'White Rice'], 'tags': ['chicken', 'orange', 'asian']},
    {'name': 'Beef Barley Soup', 'category': 'Soup', 'difficulty': 'medium', 'prep_time': '1 hour 30 minutes', 'servings': 6, 'main': ['Beef Round'], 'secondary': ['Potatoes', 'Onions', 'Bottled Water', 'Garlic', 'Thyme', 'Salt'], 'tags': ['soup', 'beef', 'barley']},
    {'name': 'Breakfast Burrito', 'category': 'Breakfast', 'difficulty': 'easy', 'prep_time': '15 minutes', 'servings': 2, 'main': ['Eggs', 'Local Cheese'], 'secondary': ['Onions', 'Tomatoes', 'Butter', 'Salt'], 'tags': ['breakfast', 'burrito', 'eggs']},
    {'name': 'Lettuce Wraps', 'category': 'Appetizer', 'difficulty': 'easy', 'prep_time': '15 minutes', 'servings': 4, 'main': ['Lettuce'], 'secondary': ['Onions', 'Garlic', 'Soy Sauce'], 'tags': ['wraps', 'lettuce', 'healthy']},
    {'name': 'Apple Pie', 'category': 'Dessert', 'difficulty': 'hard', 'prep_time': '1 hour 45 minutes', 'servings': 8, 'main': ['Apples'], 'secondary': ['Flour', 'Sugar', 'Butter'], 'tags': ['pie', 'apple', 'baked']},
    {'name': 'Orange Salad', 'category': 'Salad', 'difficulty': 'easy', 'prep_time': '10 minutes', 'servings': 4, 'main': ['Oranges', 'Lettuce'], 'secondary': ['Onions', 'Olive Oil', 'Honey'], 'tags': ['salad', 'orange', 'fresh']},
]

def get_random_amount(ingredient):
    if ingredient in ingredients_pool:
        return random.choice(ingredients_pool[ingredient])
    elif ingredient in pantry_items:
        return random.choice(pantry_items[ingredient])
    else:
        return '1 cup'

# Generate CSV
headers = ['name', 'category', 'difficulty', 'prep_time', 'servings', 'ingredients', 'tags', 'featured', 'image', 'calories', 'protein', 'carbs', 'fat', 'fiber']

with open('excel docs/Recipes.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    
    for idx, recipe in enumerate(recipes):
        # Build ingredients list with amounts
        ingredients_with_amounts = []
        for ing in recipe['main']:
            amount = get_random_amount(ing)
            ingredients_with_amounts.append(f'{amount} {ing}')
        
        for ing in recipe['secondary']:
            amount = get_random_amount(ing)
            ingredients_with_amounts.append(f'{amount} {ing}')
        
        # Create recipe row
        row = {
            'name': recipe['name'],
            'category': recipe['category'],
            'difficulty': recipe['difficulty'],
            'prep_time': recipe['prep_time'],
            'servings': recipe['servings'],
            'ingredients': json.dumps(ingredients_with_amounts),
            'tags': json.dumps(recipe['tags']),
            'featured': 'True' if idx < 20 else 'False',
            'image': '',
            'calories': '',
            'protein': '',
            'carbs': '',
            'fat': '',
            'fiber': ''
        }
        
        writer.writerow(row)

print(f'✓ Created Recipes.csv with {len(recipes)} recipes using Kansas ingredients')
print(f'✓ All ingredients include amounts (e.g., "1 lb Chicken Fillets", "2 cups White Rice")')
print(f'✓ Recipe categories: Chicken ({sum(1 for r in recipes if "chicken" in r["name"].lower() or "chicken" in " ".join(r["tags"]))}), Beef, Vegetables, Breakfast, Desserts, and more!')
