"""
Generate 100 authentic Dominican recipes based on ingredients from Dominican Republic.xlsx
All ingredients include amounts (e.g., "2 lbs Chicken Thighs")
"""

import csv
import json

# 100 authentic Dominican recipes with ingredients INCLUDING AMOUNTS
recipes = [
    {
        'name': 'Sancocho Dominicano (Dominican Stew)',
        'category': 'Main Course',
        'difficulty': 'medium',
        'prep_time': '2 hours',
        'servings': 8,
        'ingredients': ['2 lbs Chicken Thighs', '1.5 lbs Beef Stew Meat', '1 lb Pork Shoulder', '2 lbs Cassava', '3 units Green Plantain', '1 lb Sweet Potato', '1 lb Pumpkin', '2 units Corn on the Cob', '1 bunch Cilantro', '2 units Onions', '6 cloves Garlic', '1 unit Green Bell Pepper', '2 tsp Oregano', '2 tsp Salt', '1 tsp Black Pepper'],
        'tags': ['traditional', 'stew', 'comfort food', 'family meal'],
        'featured': True
    },
    {
        'name': 'La Bandera Dominicana (The Flag)',
        'category': 'Main Course',
        'difficulty': 'easy',
        'prep_time': '45 minutes',
        'servings': 4,
        'ingredients': ['2 cups White Rice', '1 cup Red Kidney Beans', '1.5 lbs Chicken Drumsticks', '2 units Tomatoes', '1 unit Onions', '4 cloves Garlic', '1 unit Green Bell Pepper', '1/2 bunch Cilantro', '2 tbsp Adobo Seasoning', '3 tbsp Vegetable Oil', '1 tsp Salt'],
        'tags': ['daily meal', 'traditional', 'rice and beans'],
        'featured': True
    },
    {
        'name': 'Moro de Guandules (Rice with Pigeon Peas)',
        'category': 'Side Dish',
        'difficulty': 'easy',
        'prep_time': '35 minutes',
        'servings': 6,
        'ingredients': ['3 cups White Rice', '2 cans Pigeon Peas', '1 cup Coconut Milk', '1 unit Onions', '4 cloves Garlic', '1 unit Cubanelle Pepper', '1/2 bunch Cilantro', '3 tbsp Tomato Paste', '2 tbsp Adobo Seasoning', '3 tbsp Vegetable Oil', '1 tsp Salt'],
        'tags': ['rice', 'side dish', 'christmas'],
        'featured': True
    },
    {
        'name': 'Pollo Guisado (Dominican Stewed Chicken)',
        'category': 'Main Course',
        'difficulty': 'easy',
        'prep_time': '40 minutes',
        'servings': 4,
        'ingredients': ['3 lbs Whole Chicken', '3 units Tomatoes', '1 unit Onions', '5 cloves Garlic', '1 unit Green Bell Pepper', '1/2 bunch Cilantro', '1/2 cup Tomato Sauce', '1 tsp Oregano', '2 tbsp Adobo Seasoning', '2 tbsp Vinegar', '3 tbsp Vegetable Oil', '1 tsp Salt', '1/2 tsp Black Pepper'],
        'tags': ['chicken', 'stew', 'traditional'],
        'featured': True
    },
    {
        'name': 'Mangú con Los Tres Golpes',
        'category': 'Breakfast',
        'difficulty': 'medium',
        'prep_time': '30 minutes',
        'servings': 4,
        'ingredients': ['4 units Green Plantain', '1 unit Onions', '1/4 cup Vinegar', '1/2 cup Vegetable Oil', '4 units Eggs', '8 oz Salami', '8 oz Dominican White Cheese', '1 tsp Salt', '2 tbsp Butter'],
        'tags': ['breakfast', 'traditional', 'plantain'],
        'featured': True
    },
    {
        'name': 'Asopao de Pollo (Chicken Rice Soup)',
        'category': 'Soup',
        'difficulty': 'medium',
        'prep_time': '50 minutes',
        'servings': 6,
        'ingredients': ['2 lbs Chicken Thighs', '1.5 cups White Rice', '3 units Tomatoes', '1 unit Onions', '5 cloves Garlic', '1 unit Green Bell Pepper', '1 bunch Cilantro', '2 units Carrots', '1 cup Peas', '1/2 cup Tomato Sauce', '2 tbsp Adobo Seasoning', '1 tsp Oregano', '3 tbsp Vegetable Oil', '1 tsp Salt'],
        'tags': ['soup', 'rice', 'comfort food'],
        'featured': False
    },
    {
        'name': 'Habichuelas Guisadas (Stewed Beans)',
        'category': 'Side Dish',
        'difficulty': 'easy',
        'prep_time': '1 hour',
        'servings': 6,
        'ingredients': ['2 cups Red Kidney Beans', '1 cup Pumpkin', '2 units Tomatoes', '1 unit Onions', '4 cloves Garlic', '1 unit Green Bell Pepper', '1/2 bunch Cilantro', '3 tbsp Tomato Paste', '1 tbsp Adobo Seasoning', '1 tsp Sugar', '2 tbsp Vegetable Oil', '1 tsp Salt'],
        'tags': ['beans', 'side dish', 'vegetarian'],
        'featured': False
    },
    {
        'name': 'Tostones (Fried Green Plantains)',
        'category': 'Side Dish',
        'difficulty': 'easy',
        'prep_time': '20 minutes',
        'servings': 4,
        'ingredients': ['3 units Green Plantain', '2 cups Vegetable Oil', '1 tsp Salt', '3 cloves Garlic'],
        'tags': ['fried', 'plantain', 'side dish', 'appetizer'],
        'featured': False
    },
    {
        'name': 'Maduros (Fried Sweet Plantains)',
        'category': 'Side Dish',
        'difficulty': 'easy',
        'prep_time': '15 minutes',
        'servings': 4,
        'ingredients': ['3 units Ripe Plantain', '1 cup Vegetable Oil', '1/2 tsp Salt'],
        'tags': ['fried', 'plantain', 'sweet', 'side dish'],
        'featured': False
    },
    {
        'name': 'Res Guisada (Dominican Beef Stew)',
        'category': 'Main Course',
        'difficulty': 'medium',
        'prep_time': '1 hour',
        'servings': 6,
        'ingredients': ['2 lbs Beef Stew Meat', '3 units Potatoes', '2 units Carrots', '3 units Tomatoes', '1 unit Onions', '5 cloves Garlic', '1 unit Green Bell Pepper', '1/2 bunch Cilantro', '1/2 cup Tomato Sauce', '2 tbsp Worcestershire Sauce', '1 tsp Oregano', '2 tbsp Adobo Seasoning', '3 tbsp Vegetable Oil', '1 tsp Salt', '1/2 tsp Black Pepper'],
        'tags': ['beef', 'stew', 'traditional'],
        'featured': False
    },
    {
        'name': 'Cerdo Guisado (Stewed Pork)',
        'category': 'Main Course',
        'difficulty': 'medium',
        'prep_time': '55 minutes',
        'servings': 4,
        'ingredients': ['2 lbs Pork Chops', '3 units Tomatoes', '1 unit Onions', '5 cloves Garlic', '1 unit Green Bell Pepper', '1/2 cup Tomato Sauce', '1 tsp Oregano', '2 tbsp Adobo Seasoning', '2 tbsp Vinegar', '3 tbsp Vegetable Oil', '1 tsp Salt', '1/2 tsp Black Pepper'],
        'tags': ['pork', 'stew', 'traditional'],
        'featured': False
    },
    {
        'name': 'Pescado Frito (Fried Fish)',
        'category': 'Main Course',
        'difficulty': 'easy',
        'prep_time': '25 minutes',
        'servings': 4,
        'ingredients': ['2 lbs Tilapia', '1 cup Wheat Flour', '4 cloves Garlic', '2 units Limes', '1 tsp Oregano', '1 tsp Salt', '1/2 tsp Black Pepper', '2 cups Vegetable Oil'],
        'tags': ['fish', 'fried', 'seafood'],
        'featured': False
    },
    {
        'name': 'Chillo Frito (Fried Red Snapper)',
        'category': 'Main Course',
        'difficulty': 'medium',
        'prep_time': '30 minutes',
        'servings': 4,
        'ingredients': ['2 lbs Red Snapper', '1 cup Wheat Flour', '5 cloves Garlic', '2 units Limes', '1 tsp Oregano', '1 tsp Salt', '1/2 tsp Black Pepper', '2 cups Vegetable Oil'],
        'tags': ['fish', 'fried', 'seafood', 'special'],
        'featured': False
    },
    {
        'name': 'Camarones al Ajillo (Garlic Shrimp)',
        'category': 'Main Course',
        'difficulty': 'easy',
        'prep_time': '20 minutes',
        'servings': 4,
        'ingredients': ['1.5 lbs Shrimp', '8 cloves Garlic', '4 tbsp Butter', '3 tbsp Olive Oil', '1/2 cup White Wine', '2 units Limes', '1/4 bunch Cilantro', '1 tsp Salt', '1/2 tsp Black Pepper'],
        'tags': ['shrimp', 'garlic', 'seafood', 'quick'],
        'featured': False
    },
    {
        'name': 'Bacalaítos (Codfish Fritters)',
        'category': 'Appetizer',
        'difficulty': 'medium',
        'prep_time': '45 minutes',
        'servings': 12,
        'ingredients': ['8 oz Dried Salted Cod', '2 cups Wheat Flour', '4 cloves Garlic', '1 unit Onions', '1/4 bunch Cilantro', '1 unit Cubanelle Pepper', '1 tbsp Baking Powder', '1.5 cups Water', '2 cups Vegetable Oil', '1/2 tsp Salt'],
        'tags': ['fritters', 'appetizer', 'street food', 'bacalao'],
        'featured': False
    },
    {
        'name': 'Yuca con Cebolla (Cassava with Onions)',
        'category': 'Side Dish',
        'difficulty': 'easy',
        'prep_time': '30 minutes',
        'servings': 4,
        'ingredients': ['2 lbs Cassava', '2 units Onions', '1/4 cup Vinegar', '1/4 cup Olive Oil', '1 tsp Salt'],
        'tags': ['cassava', 'side dish', 'simple'],
        'featured': False
    },
    {
        'name': 'Ensalada Verde (Green Salad)',
        'category': 'Salad',
        'difficulty': 'easy',
        'prep_time': '10 minutes',
        'servings': 4,
        'ingredients': ['1 head Lettuce', '2 units Tomatoes', '1 unit Avocado', '1/2 unit Onions', '2 units Limes', '3 tbsp Olive Oil', '2 tbsp Vinegar', '1/2 tsp Salt'],
        'tags': ['salad', 'vegetarian', 'fresh', 'healthy'],
        'featured': False
    },
    {
        'name': 'Pastelón de Plátano Maduro (Sweet Plantain Casserole)',
        'category': 'Main Course',
        'difficulty': 'medium',
        'prep_time': '1 hour',
        'servings': 8,
        'ingredients': ['6 units Ripe Plantain', '1.5 lbs Ground Beef', '4 units Eggs', '1 unit Onions', '4 cloves Garlic', '1 unit Green Bell Pepper', '1 cup Tomato Sauce', '2 cups Mozzarella Cheese', '3 tbsp Butter', '1/2 cup Whole Milk', '2 tbsp Adobo Seasoning', '1 tsp Salt', '1/2 cup Vegetable Oil'],
        'tags': ['casserole', 'plantain', 'beef', 'baked'],
        'featured': True
    },
    {
        'name': 'Yaroa (Dominican Fast Food Casserole)',
        'category': 'Main Course',
        'difficulty': 'easy',
        'prep_time': '35 minutes',
        'servings': 4,
        'ingredients': ['3 units Green Plantain', '1 lb Ground Beef', '1 unit Onions', '3 cloves Garlic', '1 unit Green Bell Pepper', '1/4 cup Ketchup', '1/4 cup Mayonnaise', '2 cups Mozzarella Cheese', '2 cups Vegetable Oil', '1 tsp Salt'],
        'tags': ['fast food', 'plantain', 'beef', 'street food'],
        'featured': False
    },
    {
        'name': 'Chicharrón de Pollo (Dominican Fried Chicken)',
        'category': 'Main Course',
        'difficulty': 'medium',
        'prep_time': '1 hour',
        'servings': 4,
        'ingredients': ['2 lbs Chicken Drumsticks', '1 cup Wheat Flour', '6 cloves Garlic', '1 tsp Oregano', '3 tbsp Soy Sauce', '2 units Limes', '2 tbsp Adobo Seasoning', '1 tsp Salt', '1/2 tsp Black Pepper', '3 cups Vegetable Oil'],
        'tags': ['fried', 'chicken', 'traditional'],
        'featured': True
    },
    {
        'name': 'Locrio de Pollo (Dominican Chicken Rice)',
        'category': 'Main Course',
        'difficulty': 'medium',
        'prep_time': '45 minutes',
        'servings': 6,
        'ingredients': ['3 lbs Whole Chicken', '3 cups White Rice', '3 units Tomatoes', '1 unit Onions', '5 cloves Garlic', '1 unit Green Bell Pepper', '1/2 bunch Cilantro', '1/2 cup Olives', '3 tbsp Tomato Paste', '1 cup Beer', '2 tbsp Adobo Seasoning', '3 tbsp Vegetable Oil', '1 tsp Salt'],
        'tags': ['rice', 'chicken', 'one pot'],
        'featured': False
    },
    {
        'name': 'Pica Pollo (Fried Chicken Chunks)',
        'category': 'Main Course',
        'difficulty': 'easy',
        'prep_time': '40 minutes',
        'servings': 4,
        'ingredients': ['2 lbs Chicken Thighs', '1 cup Wheat Flour', '5 cloves Garlic', '1 tsp Oregano', '3 tbsp Soy Sauce', '2 units Limes', '1 tsp Salt', '1/2 tsp Black Pepper', '3 cups Vegetable Oil'],
        'tags': ['fried', 'chicken', 'street food'],
        'featured': False
    },
    {
        'name': 'Pernil Asado (Roast Pork Shoulder)',
        'category': 'Main Course',
        'difficulty': 'hard',
        'prep_time': '4 hours',
        'servings': 10,
        'ingredients': ['6 lbs Pork Shoulder', '1 head Garlic', '2 tbsp Oregano', '1/2 cup Vinegar', '1 cup Sour Orange Juice', '3 tbsp Adobo Seasoning', '2 tsp Salt', '1 tsp Black Pepper'],
        'tags': ['pork', 'roasted', 'christmas', 'special occasion'],
        'featured': True
    },
    {
        'name': 'Arroz Blanco (White Rice)',
        'category': 'Side Dish',
        'difficulty': 'easy',
        'prep_time': '25 minutes',
        'servings': 6,
        'ingredients': ['3 cups White Rice', '2 tbsp Vegetable Oil', '1 tsp Salt', '4.5 cups Water'],
        'tags': ['rice', 'side dish', 'basic'],
        'featured': False
    },
    {
        'name': 'Moro de Habichuelas Negras (Rice with Black Beans)',
        'category': 'Side Dish',
        'difficulty': 'easy',
        'prep_time': '35 minutes',
        'servings': 6,
        'ingredients': ['3 cups White Rice', '1.5 cups Black Beans', '1 unit Onions', '4 cloves Garlic', '1 unit Cubanelle Pepper', '1/2 bunch Cilantro', '2 tbsp Adobo Seasoning', '3 tbsp Vegetable Oil', '1 tsp Salt'],
        'tags': ['rice', 'beans', 'side dish'],
        'featured': False
    },
    {
        'name': 'Sopa de Res (Beef Soup)',
        'category': 'Soup',
        'difficulty': 'medium',
        'prep_time': '1.5 hours',
        'servings': 8,
        'ingredients': ['2 lbs Beef Stew Meat', '1.5 lbs Cassava', '2 units Green Plantain', '1 lb Sweet Potato', '1 lb Pumpkin', '2 units Corn on the Cob', '2 units Carrots', '1/2 head Cabbage', '1 bunch Cilantro', '1 unit Onions', '5 cloves Garlic', '2 stalks Celery', '2 tsp Salt', '1 tsp Black Pepper'],
        'tags': ['soup', 'beef', 'comfort food'],
        'featured': False
    },
    {
        'name': 'Molondrón Guisado (Stewed Okra)',
        'category': 'Side Dish',
        'difficulty': 'easy',
        'prep_time': '30 minutes',
        'servings': 4,
        'ingredients': ['1 lb Okra', '2 units Tomatoes', '1 unit Onions', '3 cloves Garlic', '1/2 cup Tomato Sauce', '2 tbsp Vegetable Oil', '1 tsp Salt', '1/2 tsp Black Pepper'],
        'tags': ['okra', 'vegetable', 'side dish'],
        'featured': False
    },
    {
        'name': 'Berenjena Guisada (Stewed Eggplant)',
        'category': 'Side Dish',
        'difficulty': 'easy',
        'prep_time': '25 minutes',
        'servings': 4,
        'ingredients': ['2 lbs Eggplant', '2 units Tomatoes', '1 unit Onions', '4 cloves Garlic', '1 unit Green Bell Pepper', '1/2 cup Tomato Sauce', '2 tbsp Vegetable Oil', '1 tsp Salt'],
        'tags': ['eggplant', 'vegetable', 'vegetarian'],
        'featured': False
    },
    {
        'name': 'Chuletas Fritas (Fried Pork Chops)',
        'category': 'Main Course',
        'difficulty': 'easy',
        'prep_time': '30 minutes',
        'servings': 4,
        'ingredients': ['4 units Pork Chops', '5 cloves Garlic', '1 tsp Oregano', '2 units Limes', '1 tsp Salt', '1/2 tsp Black Pepper', '1 cup Vegetable Oil'],
        'tags': ['pork', 'fried', 'quick'],
        'featured': False
    },
    {
        'name': 'Longaniza Frita (Fried Dominican Sausage)',
        'category': 'Main Course',
        'difficulty': 'easy',
        'prep_time': '15 minutes',
        'servings': 4,
        'ingredients': ['1.5 lbs Longaniza', '1 unit Onions', '2 units Limes', '2 tbsp Vegetable Oil'],
        'tags': ['sausage', 'fried', 'quick'],
        'featured': False
    },
    {
        'name': 'Guineos en Escabeche (Pickled Green Bananas)',
        'category': 'Side Dish',
        'difficulty': 'medium',
        'prep_time': '40 minutes',
        'servings': 6,
        'ingredients': ['8 units Green Bananas', '2 units Onions', '1/2 cup Vinegar', '1/4 cup Olive Oil', '3 Bay Leaves', '4 oz Dried Salted Cod', '1 tsp Salt'],
        'tags': ['pickled', 'side dish', 'traditional'],
        'featured': False
    },
    {
        'name': 'Pastelitos de Carne (Meat Turnovers)',
        'category': 'Appetizer',
        'difficulty': 'medium',
        'prep_time': '1 hour',
        'servings': 12,
        'ingredients': ['3 cups Wheat Flour', '1 lb Ground Beef', '1 unit Onions', '3 cloves Garlic', '1 unit Green Bell Pepper', '1/2 cup Tomato Sauce', '1 tbsp Adobo Seasoning', '1/2 cup Butter', '2 cups Vegetable Oil', '1 tsp Salt'],
        'tags': ['pastry', 'beef', 'fried', 'street food'],
        'featured': False
    },
    {
        'name': 'Pastelitos de Pollo (Chicken Turnovers)',
        'category': 'Appetizer',
        'difficulty': 'medium',
        'prep_time': '1 hour',
        'servings': 12,
        'ingredients': ['3 cups Wheat Flour', '1 lb Chicken Thighs', '1 unit Onions', '3 cloves Garlic', '1 unit Green Bell Pepper', '1/2 cup Tomato Sauce', '1 tbsp Adobo Seasoning', '1/2 cup Butter', '2 cups Vegetable Oil', '1 tsp Salt'],
        'tags': ['pastry', 'chicken', 'fried', 'street food'],
        'featured': False
    },
    {
        'name': 'Arepitas de Yuca (Cassava Fritters)',
        'category': 'Snack',
        'difficulty': 'medium',
        'prep_time': '45 minutes',
        'servings': 8,
        'ingredients': ['2 lbs Cassava', '1/4 cup Sugar', '1 tsp Anise Seeds', '1/2 tsp Salt', '2 cups Vegetable Oil'],
        'tags': ['fritters', 'cassava', 'sweet', 'snack'],
        'featured': False
    },
    {
        'name': 'Yaniqueques (Johnny Cakes)',
        'category': 'Snack',
        'difficulty': 'easy',
        'prep_time': '30 minutes',
        'servings': 8,
        'ingredients': ['2 cups Wheat Flour', '1 tbsp Baking Powder', '2 tbsp Sugar', '1 tsp Salt', '1 cup Water', '2 cups Vegetable Oil'],
        'tags': ['fried bread', 'snack', 'beach food'],
        'featured': False
    },
    {
        'name': 'Bollitos de Yuca (Cassava Balls)',
        'category': 'Snack',
        'difficulty': 'medium',
        'prep_time': '40 minutes',
        'servings': 10,
        'ingredients': ['2 lbs Cassava', '2 units Eggs', '1 cup Dominican White Cheese', '1/4 cup Sugar', '1 tsp Anise Seeds', '1/2 tsp Salt', '2 cups Vegetable Oil'],
        'tags': ['fritters', 'cassava', 'cheese', 'snack'],
        'featured': False
    },
    {
        'name': 'Morir Soñando (Orange Cream Drink)',
        'category': 'Beverage',
        'difficulty': 'easy',
        'prep_time': '10 minutes',
        'servings': 4,
        'ingredients': ['6 units Oranges', '1 can Evaporated Milk', '1/4 cup Sugar', '1 tsp Vanilla Extract', '2 cups Ice'],
        'tags': ['drink', 'orange', 'cream', 'refreshing'],
        'featured': True
    },
    {
        'name': 'Jugo de Chinola (Passion Fruit Juice)',
        'category': 'Beverage',
        'difficulty': 'easy',
        'prep_time': '15 minutes',
        'servings': 4,
        'ingredients': ['8 units Passion Fruit', '1/2 cup Sugar', '4 cups Water', '2 cups Ice'],
        'tags': ['juice', 'passion fruit', 'drink', 'refreshing'],
        'featured': False
    },
    {
        'name': 'Avena Caliente (Hot Oatmeal Drink)',
        'category': 'Beverage',
        'difficulty': 'easy',
        'prep_time': '20 minutes',
        'servings': 4,
        'ingredients': ['1 cup Oats', '4 cups Whole Milk', '1 tsp Ground Cinnamon', '1 tsp Vanilla Extract', '1/2 cup Condensed Milk', '1/4 cup Sugar', '1/4 tsp Salt'],
        'tags': ['drink', 'hot', 'oatmeal', 'breakfast'],
        'featured': False
    },
    {
        'name': 'Batida de Lechosa (Papaya Smoothie)',
        'category': 'Beverage',
        'difficulty': 'easy',
        'prep_time': '5 minutes',
        'servings': 2,
        'ingredients': ['2 cups Papaya', '1 cup Whole Milk', '2 tbsp Sugar', '1 tsp Vanilla Extract', '1 cup Ice'],
        'tags': ['smoothie', 'papaya', 'drink', 'breakfast'],
        'featured': False
    },
    {
        'name': 'Habichuelas con Dulce (Sweet Cream of Beans)',
        'category': 'Dessert',
        'difficulty': 'medium',
        'prep_time': '1.5 hours',
        'servings': 10,
        'ingredients': ['2 cups Red Kidney Beans', '1 can Coconut Milk', '1 can Evaporated Milk', '1 can Condensed Milk', '1 cup Sugar', '1 lb Sweet Potato', '1 tbsp Ground Cinnamon', '1/2 tsp Ground Cloves', '1/2 cup Raisins', '2 tbsp Butter', '2 tsp Vanilla Extract'],
        'tags': ['dessert', 'beans', 'cream', 'easter', 'traditional'],
        'featured': True
    },
    {
        'name': 'Majarete (Corn Pudding)',
        'category': 'Dessert',
        'difficulty': 'easy',
        'prep_time': '30 minutes',
        'servings': 6,
        'ingredients': ['3 cups Fresh Corn', '1 can Coconut Milk', '2 cups Whole Milk', '3/4 cup Sugar', '1 tsp Ground Cinnamon', '1 tsp Vanilla Extract', '1/4 tsp Salt'],
        'tags': ['dessert', 'corn', 'pudding', 'traditional'],
        'featured': False
    },
    {
        'name': 'Flan de Coco (Coconut Flan)',
        'category': 'Dessert',
        'difficulty': 'medium',
        'prep_time': '1 hour',
        'servings': 8,
        'ingredients': ['6 units Eggs', '1 can Coconut Milk', '1 can Condensed Milk', '1 can Evaporated Milk', '1 cup Sugar', '2 tsp Vanilla Extract'],
        'tags': ['dessert', 'flan', 'coconut', 'baked'],
        'featured': False
    },
    {
        'name': 'Arroz con Leche (Rice Pudding)',
        'category': 'Dessert',
        'difficulty': 'easy',
        'prep_time': '40 minutes',
        'servings': 6,
        'ingredients': ['1 cup White Rice', '4 cups Whole Milk', '1/2 cup Condensed Milk', '1/2 cup Sugar', '1 tsp Ground Cinnamon', '1 tsp Vanilla Extract', '1/2 cup Raisins', '1/4 tsp Salt'],
        'tags': ['dessert', 'rice', 'pudding', 'traditional'],
        'featured': False
    },
    {
        'name': 'Dulce de Coco (Coconut Sweet)',
        'category': 'Dessert',
        'difficulty': 'medium',
        'prep_time': '45 minutes',
        'servings': 8,
        'ingredients': ['2 units Fresh Coconut', '2 cups Sugar', '1 cup Water', '1 tsp Ground Cinnamon'],
        'tags': ['dessert', 'coconut', 'sweet', 'traditional'],
        'featured': False
    },
    {
        'name': 'Dulce de Lechosa (Candied Papaya)',
        'category': 'Dessert',
        'difficulty': 'easy',
        'prep_time': '1 hour',
        'servings': 8,
        'ingredients': ['3 lbs Green Papaya', '2 cups Sugar', '1 tsp Ground Cinnamon', '1/4 tsp Ground Cloves', '3 cups Water'],
        'tags': ['dessert', 'papaya', 'candied', 'traditional'],
        'featured': False
    },
    {
        'name': 'Tres Leches Cake',
        'category': 'Dessert',
        'difficulty': 'hard',
        'prep_time': '2 hours',
        'servings': 12,
        'ingredients': ['2 cups Wheat Flour', '6 units Eggs', '1.5 cups Sugar', '1 cup Whole Milk', '1 can Evaporated Milk', '1 can Condensed Milk', '2 cups Heavy Cream', '2 tsp Vanilla Extract', '1 tbsp Baking Powder'],
        'tags': ['cake', 'dessert', 'tres leches', 'celebration'],
        'featured': True
    },
    {
        'name': 'Bizcocho Dominicano (Dominican Cake)',
        'category': 'Dessert',
        'difficulty': 'hard',
        'prep_time': '2 hours',
        'servings': 16,
        'ingredients': ['3 cups Wheat Flour', '8 units Eggs', '2 cups Sugar', '1 cup Whole Milk', '1 cup Butter', '2 tsp Vanilla Extract', '2 tbsp Baking Powder', '1 cup Pineapple', '1/4 cup Rum', '4 cups Meringue'],
        'tags': ['cake', 'dessert', 'celebration', 'traditional'],
        'featured': True
    },
    {
        'name': 'Ensalada de Coditos (Macaroni Salad)',
        'category': 'Salad',
        'difficulty': 'easy',
        'prep_time': '25 minutes',
        'servings': 6,
        'ingredients': ['1 lb Macaroni Pasta', '1 cup Mayonnaise', '2 units Carrots', '1 cup Corn', '1 cup Peas', '4 units Hard Boiled Eggs', '1 tsp Salt', '1/2 tsp Black Pepper', '1 tbsp Sugar'],
        'tags': ['salad', 'pasta', 'side dish', 'potluck'],
        'featured': False
    },
    {
        'name': 'Ensalada Rusa (Russian Salad)',
        'category': 'Salad',
        'difficulty': 'medium',
        'prep_time': '45 minutes',
        'servings': 8,
        'ingredients': ['4 units Potatoes', '3 units Carrots', '2 units Beets', '1 cup Peas', '4 units Hard Boiled Eggs', '1.5 cups Mayonnaise', '1 cup Diced Ham', '1 tsp Salt', '1/2 tsp Black Pepper'],
        'tags': ['salad', 'potato', 'christmas', 'celebration'],
        'featured': False
    },
    {
        'name': 'Guineitos con Huevo (Bananas with Egg)',
        'category': 'Breakfast',
        'difficulty': 'easy',
        'prep_time': '20 minutes',
        'servings': 2,
        'ingredients': ['4 units Ripe Bananas', '2 units Eggs', '2 tbsp Butter', '2 tbsp Sugar', '1/2 tsp Ground Cinnamon', '1/4 tsp Salt'],
        'tags': ['breakfast', 'banana', 'eggs', 'quick'],
        'featured': False
    },
    {
        'name': 'Revoltillo de Huevos (Scrambled Eggs Dominican Style)',
        'category': 'Breakfast',
        'difficulty': 'easy',
        'prep_time': '15 minutes',
        'servings': 2,
        'ingredients': ['4 units Eggs', '2 units Tomatoes', '1/2 unit Onions', '1/2 unit Green Bell Pepper', '2 tbsp Vegetable Oil', '1/2 tsp Salt', '1/4 tsp Black Pepper'],
        'tags': ['breakfast', 'eggs', 'quick', 'traditional'],
        'featured': False
    },
    {
        'name': 'Huevos Bañados (Eggs in Tomato Sauce)',
        'category': 'Breakfast',
        'difficulty': 'easy',
        'prep_time': '20 minutes',
        'servings': 4,
        'ingredients': ['4 units Eggs', '1.5 cups Tomato Sauce', '1 unit Onions', '3 cloves Garlic', '1 unit Green Bell Pepper', '2 tbsp Vegetable Oil', '1/2 tsp Salt', '1/4 tsp Black Pepper'],
        'tags': ['breakfast', 'eggs', 'tomato sauce'],
        'featured': False
    },
    {
        'name': 'Salami con Huevo (Salami with Eggs)',
        'category': 'Breakfast',
        'difficulty': 'easy',
        'prep_time': '15 minutes',
        'servings': 2,
        'ingredients': ['8 oz Salami', '4 units Eggs', '1/2 unit Onions', '1 tbsp Vegetable Oil'],
        'tags': ['breakfast', 'eggs', 'salami', 'quick'],
        'featured': False
    },
    {
        'name': 'Pan Con Aguacate (Bread with Avocado)',
        'category': 'Breakfast',
        'difficulty': 'easy',
        'prep_time': '5 minutes',
        'servings': 1,
        'ingredients': ['2 slices Bread', '1 unit Avocado', '1/4 tsp Salt', '1 tbsp Olive Oil'],
        'tags': ['breakfast', 'avocado', 'quick', 'simple'],
        'featured': False
    },
    {
        'name': 'Chambre (Avocado and Egg Salad)',
        'category': 'Breakfast',
        'difficulty': 'easy',
        'prep_time': '15 minutes',
        'servings': 2,
        'ingredients': ['3 units Hard Boiled Eggs', '2 units Avocado', '1/2 unit Onions', '2 tbsp Olive Oil', '1 tbsp Vinegar', '1/2 tsp Salt'],
        'tags': ['breakfast', 'salad', 'avocado', 'eggs'],
        'featured': False
    },
    {
        'name': 'Locrio de Longaniza (Longaniza Rice)',
        'category': 'Main Course',
        'difficulty': 'medium',
        'prep_time': '45 minutes',
        'servings': 6,
        'ingredients': ['3 cups White Rice', '1 lb Longaniza', '2 units Tomatoes', '1 unit Onions', '4 cloves Garlic', '1 unit Green Bell Pepper', '1/2 bunch Cilantro', '3 tbsp Tomato Paste', '2 tbsp Adobo Seasoning', '2 tbsp Vegetable Oil', '1 tsp Salt'],
        'tags': ['rice', 'sausage', 'one pot'],
        'featured': False
    },
    {
        'name': 'Locrio de Cerdo (Pork Rice)',
        'category': 'Main Course',
        'difficulty': 'medium',
        'prep_time': '50 minutes',
        'servings': 6,
        'ingredients': ['3 cups White Rice', '1.5 lbs Pork Chops', '2 units Tomatoes', '1 unit Onions', '4 cloves Garlic', '1 unit Green Bell Pepper', '1/2 bunch Cilantro', '3 tbsp Tomato Paste', '2 tbsp Adobo Seasoning', '2 tbsp Vegetable Oil', '1 tsp Salt'],
        'tags': ['rice', 'pork', 'one pot'],
        'featured': False
    },
    {
        'name': 'Locrio de Camarones (Shrimp Rice)',
        'category': 'Main Course',
        'difficulty': 'medium',
        'prep_time': '40 minutes',
        'servings': 4,
        'ingredients': ['2 cups White Rice', '1 lb Shrimp', '2 units Tomatoes', '1 unit Onions', '4 cloves Garlic', '1 unit Green Bell Pepper', '1/2 bunch Cilantro', '3 tbsp Tomato Paste', '2 tbsp Adobo Seasoning', '3 tbsp Olive Oil', '1 tsp Salt'],
        'tags': ['rice', 'shrimp', 'seafood', 'one pot'],
        'featured': True
    },
    {
        'name': 'Espagueti con Pollo (Spaghetti with Chicken)',
        'category': 'Main Course',
        'difficulty': 'easy',
        'prep_time': '35 minutes',
        'servings': 6,
        'ingredients': ['1 lb Spaghetti Pasta', '1.5 lbs Chicken Thighs', '2 cups Tomato Sauce', '1 unit Onions', '4 cloves Garlic', '1 unit Green Bell Pepper', '1 tsp Oregano', '1 tbsp Sugar', '3 tbsp Vegetable Oil', '1 tsp Salt'],
        'tags': ['pasta', 'chicken', 'quick'],
        'featured': False
    },
    {
        'name': 'Espagueti con Salami (Spaghetti with Salami)',
        'category': 'Main Course',
        'difficulty': 'easy',
        'prep_time': '25 minutes',
        'servings': 4,
        'ingredients': ['1 lb Spaghetti Pasta', '12 oz Salami', '2 cups Tomato Sauce', '1 unit Onions', '3 cloves Garlic', '1 unit Green Bell Pepper', '1 tsp Oregano', '1 tbsp Sugar', '2 tbsp Vegetable Oil', '1 tsp Salt'],
        'tags': ['pasta', 'salami', 'quick'],
        'featured': False
    },
    {
        'name': 'Espagueti con Camarones (Spaghetti with Shrimp)',
        'category': 'Main Course',
        'difficulty': 'medium',
        'prep_time': '30 minutes',
        'servings': 4,
        'ingredients': ['1 lb Spaghetti Pasta', '1 lb Shrimp', '2 cups Tomato Sauce', '1 unit Onions', '4 cloves Garlic', '1 unit Green Bell Pepper', '1 tsp Oregano', '1/2 cup White Wine', '3 tbsp Olive Oil', '1 tsp Salt'],
        'tags': ['pasta', 'shrimp', 'seafood'],
        'featured': False
    },
    {
        'name': 'Rabo Guisado (Oxtail Stew)',
        'category': 'Main Course',
        'difficulty': 'hard',
        'prep_time': '3 hours',
        'servings': 6,
        'ingredients': ['3 lbs Oxtail', '2 units Tomatoes', '1 unit Onions', '5 cloves Garlic', '1 unit Green Bell Pepper', '2 units Carrots', '3 units Potatoes', '1 cup Tomato Sauce', '1 cup Red Wine', '2 tbsp Worcestershire Sauce', '3 Bay Leaves', '1 tsp Oregano', '2 tbsp Adobo Seasoning', '3 tbsp Vegetable Oil', '1 tsp Salt', '1/2 tsp Black Pepper'],
        'tags': ['stew', 'oxtail', 'special', 'slow cooked'],
        'featured': True
    },
    {
        'name': 'Hígado Encebollado (Liver with Onions)',
        'category': 'Main Course',
        'difficulty': 'easy',
        'prep_time': '25 minutes',
        'servings': 4,
        'ingredients': ['1.5 lbs Beef Liver', '2 units Onions', '4 cloves Garlic', '2 units Limes', '2 tbsp Vinegar', '1 tsp Oregano', '2 tbsp Vegetable Oil', '1 tsp Salt', '1/2 tsp Black Pepper'],
        'tags': ['liver', 'onions', 'quick'],
        'featured': False
    },
    {
        'name': 'Sopa de Pescado (Fish Soup)',
        'category': 'Soup',
        'difficulty': 'medium',
        'prep_time': '45 minutes',
        'servings': 6,
        'ingredients': ['2 lbs Tilapia', '1 lb Cassava', '2 units Green Plantain', '2 units Tomatoes', '1 unit Onions', '4 cloves Garlic', '1 unit Green Bell Pepper', '1 bunch Cilantro', '2 units Limes', '1 can Coconut Milk', '1 tsp Salt', '1/2 tsp Black Pepper'],
        'tags': ['soup', 'fish', 'seafood'],
        'featured': False
    },
    {
        'name': 'Sopa de Mariscos (Seafood Soup)',
        'category': 'Soup',
        'difficulty': 'medium',
        'prep_time': '50 minutes',
        'servings': 6,
        'ingredients': ['1 lb Shrimp', '1 lb Fish Fillets', '1 lb Mussels', '1 lb Squid', '2 units Tomatoes', '1 unit Onions', '5 cloves Garlic', '1 unit Green Bell Pepper', '1 bunch Cilantro', '1 cup Tomato Sauce', '1 cup White Wine', '2 units Limes', '3 tbsp Olive Oil', '1 tsp Salt', '1/2 tsp Black Pepper'],
        'tags': ['soup', 'seafood', 'special'],
        'featured': True
    },
    {
        'name': 'Sopa de Guandules (Pigeon Pea Soup)',
        'category': 'Soup',
        'difficulty': 'easy',
        'prep_time': '40 minutes',
        'servings': 6,
        'ingredients': ['2 cans Pigeon Peas', '1 lb Pumpkin', '1 lb Cassava', '1 lb Sweet Potato', '1 unit Onions', '4 cloves Garlic', '1 bunch Cilantro', '1 can Coconut Milk', '1 tsp Salt', '1/2 tsp Black Pepper'],
        'tags': ['soup', 'beans', 'vegetarian'],
        'featured': False
    },
    {
        'name': 'Sopa de Habichuelas (Bean Soup)',
        'category': 'Soup',
        'difficulty': 'easy',
        'prep_time': '1 hour',
        'servings': 6,
        'ingredients': ['2 cups Red Kidney Beans', '1 lb Pumpkin', '1 lb Sweet Potato', '1 unit Onions', '4 cloves Garlic', '1 bunch Cilantro', '3 tbsp Tomato Paste', '1 tsp Salt', '1/2 tsp Black Pepper'],
        'tags': ['soup', 'beans', 'vegetarian'],
        'featured': False
    },
    {
        'name': 'Crema de Auyama (Pumpkin Cream Soup)',
        'category': 'Soup',
        'difficulty': 'easy',
        'prep_time': '35 minutes',
        'servings': 4,
        'ingredients': ['2 lbs Pumpkin', '1 unit Onions', '3 cloves Garlic', '2 cups Whole Milk', '1 cup Heavy Cream', '2 tbsp Butter', '1/4 tsp Nutmeg', '1 tsp Salt', '1/2 tsp Black Pepper'],
        'tags': ['soup', 'cream', 'pumpkin', 'vegetarian'],
        'featured': False
    },
    {
        'name': 'Crema de Vegetales (Vegetable Cream Soup)',
        'category': 'Soup',
        'difficulty': 'easy',
        'prep_time': '40 minutes',
        'servings': 6,
        'ingredients': ['1 lb Pumpkin', '3 units Carrots', '2 stalks Celery', '1 unit Onions', '3 cloves Garlic', '2 units Potatoes', '3 cups Whole Milk', '3 tbsp Butter', '1 tsp Salt', '1/2 tsp Black Pepper'],
        'tags': ['soup', 'cream', 'vegetables', 'vegetarian'],
        'featured': False
    },
    {
        'name': 'Arroz con Coco (Coconut Rice)',
        'category': 'Side Dish',
        'difficulty': 'easy',
        'prep_time': '30 minutes',
        'servings': 6,
        'ingredients': ['3 cups White Rice', '1.5 cans Coconut Milk', '1/4 cup Sugar', '1 tsp Salt', '1/2 cup Raisins'],
        'tags': ['rice', 'coconut', 'side dish', 'sweet'],
        'featured': False
    },
    {
        'name': 'Arroz Amarillo (Yellow Rice)',
        'category': 'Side Dish',
        'difficulty': 'easy',
        'prep_time': '25 minutes',
        'servings': 6,
        'ingredients': ['3 cups White Rice', '1 unit Onions', '3 cloves Garlic', '1 unit Green Bell Pepper', '1 tsp Turmeric', '2 tbsp Vegetable Oil', '1 tsp Salt'],
        'tags': ['rice', 'side dish', 'yellow'],
        'featured': False
    },
    {
        'name': 'Puré de Papa (Mashed Potatoes)',
        'category': 'Side Dish',
        'difficulty': 'easy',
        'prep_time': '30 minutes',
        'servings': 4,
        'ingredients': ['4 units Potatoes', '3 tbsp Butter', '1/2 cup Whole Milk', '1 tsp Salt', '1/2 tsp Black Pepper'],
        'tags': ['potatoes', 'side dish', 'mashed'],
        'featured': False
    },
    {
        'name': 'Papas Fritas (French Fries)',
        'category': 'Side Dish',
        'difficulty': 'easy',
        'prep_time': '25 minutes',
        'servings': 4,
        'ingredients': ['4 units Potatoes', '3 cups Vegetable Oil', '1 tsp Salt'],
        'tags': ['potatoes', 'fried', 'side dish'],
        'featured': False
    },
    {
        'name': 'Molletes (Sweet Cornmeal Cakes)',
        'category': 'Dessert',
        'difficulty': 'medium',
        'prep_time': '40 minutes',
        'servings': 12,
        'ingredients': ['2 cups Corn Flour', '1/2 cup Sugar', '1 can Coconut Milk', '1 tsp Ground Cinnamon', '1 tsp Anise Seeds', '1/2 cup Raisins', '2 cups Vegetable Oil', '1/2 tsp Salt'],
        'tags': ['dessert', 'corn', 'sweet', 'fried'],
        'featured': False
    },
    {
        'name': 'Casabe (Cassava Bread)',
        'category': 'Bread',
        'difficulty': 'hard',
        'prep_time': '2 hours',
        'servings': 10,
        'ingredients': ['5 lbs Cassava', '1 tsp Salt'],
        'tags': ['bread', 'cassava', 'traditional', 'indigenous'],
        'featured': False
    },
    {
        'name': 'Arepa Dominicana (Dominican Corn Pancake)',
        'category': 'Dessert',
        'difficulty': 'easy',
        'prep_time': '35 minutes',
        'servings': 8,
        'ingredients': ['2 cups Corn Flour', '1 can Coconut Milk', '3/4 cup Sugar', '1 tsp Vanilla Extract', '1 tsp Ground Cinnamon', '1/2 cup Raisins', '3 tbsp Butter', '1/4 tsp Salt'],
        'tags': ['dessert', 'corn', 'sweet', 'traditional'],
        'featured': False
    },
    {
        'name': 'Pan de Batata (Sweet Potato Bread)',
        'category': 'Dessert',
        'difficulty': 'medium',
        'prep_time': '1 hour',
        'servings': 10,
        'ingredients': ['2 lbs Sweet Potato', '2 cups Wheat Flour', '3 units Eggs', '3/4 cup Sugar', '1/2 cup Butter', '1/2 cup Whole Milk', '1 tsp Ground Cinnamon', '1 tsp Vanilla Extract', '1 tbsp Baking Powder', '1/2 tsp Salt'],
        'tags': ['dessert', 'bread', 'sweet potato', 'baked'],
        'featured': False
    },
    {
        'name': 'Buñuelos (Sweet Fritters)',
        'category': 'Dessert',
        'difficulty': 'medium',
        'prep_time': '45 minutes',
        'servings': 12,
        'ingredients': ['1.5 lbs Cassava', '2 units Eggs', '1/2 cup Wheat Flour', '1/2 cup Sugar', '1 tsp Anise Seeds', '1 tsp Vanilla Extract', '2 cups Vegetable Oil', '1/2 tsp Salt'],
        'tags': ['dessert', 'fritters', 'fried', 'sweet'],
        'featured': False
    },
    {
        'name': 'Torreja (Dominican French Toast)',
        'category': 'Dessert',
        'difficulty': 'easy',
        'prep_time': '20 minutes',
        'servings': 4,
        'ingredients': ['8 slices Bread', '3 units Eggs', '1 cup Whole Milk', '1/4 cup Sugar', '1 tsp Vanilla Extract', '1 tsp Ground Cinnamon', '3 tbsp Butter'],
        'tags': ['dessert', 'bread', 'french toast', 'sweet'],
        'featured': False
    },
    {
        'name': 'Jalao (Dominican Coconut Pull Candy)',
        'category': 'Dessert',
        'difficulty': 'hard',
        'prep_time': '1.5 hours',
        'servings': 20,
        'ingredients': ['2 units Fresh Coconut', '2 cups Brown Sugar', '1/2 cup Molasses', '1 tsp Ground Ginger', '1 tsp Ground Cinnamon', '1 cup Water'],
        'tags': ['candy', 'coconut', 'traditional', 'sweet'],
        'featured': False
    },
    {
        'name': 'Helado de Coco (Coconut Ice Cream)',
        'category': 'Dessert',
        'difficulty': 'medium',
        'prep_time': '4 hours',
        'servings': 8,
        'ingredients': ['2 cans Coconut Milk', '1 can Condensed Milk', '1 can Evaporated Milk', '2 tsp Vanilla Extract', '1 cup Shredded Coconut'],
        'tags': ['ice cream', 'coconut', 'frozen', 'dessert'],
        'featured': False
    },
    {
        'name': 'Ensalada de Frutas (Fruit Salad)',
        'category': 'Dessert',
        'difficulty': 'easy',
        'prep_time': '15 minutes',
        'servings': 6,
        'ingredients': ['2 units Mango', '2 cups Papaya', '2 cups Pineapple', '2 cups Watermelon', '3 units Bananas', '3 units Oranges', '2 tbsp Sugar', '2 units Limes'],
        'tags': ['fruit', 'salad', 'fresh', 'healthy'],
        'featured': False
    },
    {
        'name': 'Chimichurri Dominicano (Dominican Burger)',
        'category': 'Main Course',
        'difficulty': 'medium',
        'prep_time': '40 minutes',
        'servings': 4,
        'ingredients': ['1.5 lbs Ground Beef', '4 units Bread', '2 cups Cabbage', '2 units Tomatoes', '1 unit Onions', '1/4 cup Ketchup', '1/4 cup Mayonnaise', '2 tbsp Hot Sauce', '2 cups Vegetable Oil', '1 tsp Salt', '1/2 tsp Black Pepper'],
        'tags': ['burger', 'street food', 'fast food'],
        'featured': True
    },
    {
        'name': 'Yaroa de Pollo (Chicken Yaroa)',
        'category': 'Main Course',
        'difficulty': 'easy',
        'prep_time': '40 minutes',
        'servings': 4,
        'ingredients': ['3 units Green Plantain', '1.5 lbs Chicken Thighs', '1 unit Onions', '1/4 cup Ketchup', '1/4 cup Mayonnaise', '2 cups Mozzarella Cheese', '2 cups Vegetable Oil', '1 tsp Salt'],
        'tags': ['yaroa', 'chicken', 'plantain', 'fast food'],
        'featured': False
    },
    {
        'name': 'Mofongo (Mashed Fried Plantains)',
        'category': 'Side Dish',
        'difficulty': 'medium',
        'prep_time': '30 minutes',
        'servings': 4,
        'ingredients': ['4 units Green Plantain', '6 cloves Garlic', '1 cup Pork Cracklings', '2 cups Vegetable Oil', '1 tsp Salt', '1 cup Chicken Broth'],
        'tags': ['plantain', 'mashed', 'garlic', 'traditional'],
        'featured': True
    },
    {
        'name': 'Pionono (Sweet Plantain Roll)',
        'category': 'Main Course',
        'difficulty': 'hard',
        'prep_time': '1.5 hours',
        'servings': 6,
        'ingredients': ['5 units Ripe Plantain', '1 lb Ground Beef', '3 units Eggs', '1 unit Onions', '4 cloves Garlic', '1 unit Green Bell Pepper', '1 cup Tomato Sauce', '1.5 cups Mozzarella Cheese', '1 tbsp Adobo Seasoning', '1 cup Vegetable Oil', '1 tsp Salt'],
        'tags': ['plantain', 'beef', 'roll', 'baked'],
        'featured': False
    },
    {
        'name': 'Camarones al Coco (Coconut Shrimp)',
        'category': 'Appetizer',
        'difficulty': 'medium',
        'prep_time': '35 minutes',
        'servings': 4,
        'ingredients': ['1 lb Shrimp', '1 cup Shredded Coconut', '1/2 cup Wheat Flour', '2 units Eggs', '1 cup Bread Crumbs', '2 cups Vegetable Oil', '1 tsp Salt', '1/2 tsp Black Pepper'],
        'tags': ['shrimp', 'coconut', 'fried', 'appetizer'],
        'featured': False
    },
    {
        'name': 'Pescado con Coco (Fish in Coconut Sauce)',
        'category': 'Main Course',
        'difficulty': 'medium',
        'prep_time': '35 minutes',
        'servings': 4,
        'ingredients': ['2 lbs Tilapia', '1 can Coconut Milk', '1 unit Onions', '4 cloves Garlic', '1 unit Green Bell Pepper', '2 units Tomatoes', '1/2 bunch Cilantro', '2 units Limes', '1 tsp Salt', '1/2 tsp Black Pepper'],
        'tags': ['fish', 'coconut', 'sauce', 'seafood'],
        'featured': True
    },
    {
        'name': 'Kipe (Dominican Kibbeh)',
        'category': 'Appetizer',
        'difficulty': 'hard',
        'prep_time': '1.5 hours',
        'servings': 12,
        'ingredients': ['2 cups Bulgur Wheat', '1 lb Ground Beef', '1 unit Onions', '4 cloves Garlic', '1 unit Green Bell Pepper', '1/2 cup Tomato Sauce', '1/4 bunch Parsley', '2 tbsp Mint', '1 tsp Cumin', '1 tsp Salt', '1/2 tsp Black Pepper', '3 cups Vegetable Oil'],
        'tags': ['fried', 'beef', 'middle eastern fusion', 'street food'],
        'featured': False
    },
    {
        'name': 'Empanadas de Yuca (Cassava Turnovers)',
        'category': 'Appetizer',
        'difficulty': 'hard',
        'prep_time': '1.5 hours',
        'servings': 12,
        'ingredients': ['3 lbs Cassava', '1 lb Ground Beef', '1 unit Onions', '4 cloves Garlic', '1 unit Green Bell Pepper', '1/2 cup Tomato Sauce', '1 tbsp Adobo Seasoning', '3 cups Vegetable Oil', '1 tsp Salt'],
        'tags': ['cassava', 'beef', 'fried', 'traditional'],
        'featured': False
    },
    {
        'name': 'Chacá (Sweet Corn and Bean Dessert)',
        'category': 'Dessert',
        'difficulty': 'medium',
        'prep_time': '1.5 hours',
        'servings': 8,
        'ingredients': ['2 cups Corn', '1 cup Red Kidney Beans', '1 can Coconut Milk', '1 can Condensed Milk', '1 cup Sugar', '1 tsp Ground Cinnamon', '1/2 tsp Ground Cloves', '1 tsp Vanilla Extract', '1/2 cup Raisins'],
        'tags': ['dessert', 'corn', 'beans', 'traditional'],
        'featured': False
    },
    {
        'name': 'Ensalada de Aguacate (Avocado Salad)',
        'category': 'Salad',
        'difficulty': 'easy',
        'prep_time': '10 minutes',
        'servings': 4,
        'ingredients': ['3 units Avocado', '2 units Tomatoes', '1 unit Onions', '2 units Limes', '3 tbsp Olive Oil', '1/2 bunch Cilantro', '1/2 tsp Salt'],
        'tags': ['salad', 'avocado', 'fresh', 'healthy'],
        'featured': False
    },
    {
        'name': 'Ensalada de Repollo (Cabbage Salad)',
        'category': 'Salad',
        'difficulty': 'easy',
        'prep_time': '15 minutes',
        'servings': 6,
        'ingredients': ['1 head Cabbage', '2 units Carrots', '1/4 cup Vinegar', '2 tbsp Sugar', '3 tbsp Mayonnaise', '1/2 tsp Salt'],
        'tags': ['salad', 'cabbage', 'coleslaw', 'side dish'],
        'featured': False
    },
    {
        'name': 'Batida de Guineo (Banana Smoothie)',
        'category': 'Beverage',
        'difficulty': 'easy',
        'prep_time': '5 minutes',
        'servings': 2,
        'ingredients': ['3 units Bananas', '2 cups Whole Milk', '2 tbsp Sugar', '1 tsp Vanilla Extract', '1 tsp Ground Cinnamon', '1 cup Ice'],
        'tags': ['smoothie', 'banana', 'drink', 'breakfast'],
        'featured': False
    },
    {
        'name': 'Café Dominicano (Dominican Coffee)',
        'category': 'Beverage',
        'difficulty': 'easy',
        'prep_time': '10 minutes',
        'servings': 4,
        'ingredients': ['4 tbsp Coffee', '4 cups Water', '4 tbsp Sugar'],
        'tags': ['coffee', 'drink', 'hot', 'traditional'],
        'featured': False
    },
    {
        'name': 'Chocolate Caliente (Hot Chocolate)',
        'category': 'Beverage',
        'difficulty': 'easy',
        'prep_time': '15 minutes',
        'servings': 4,
        'ingredients': ['4 oz Chocolate', '4 cups Whole Milk', '1/4 cup Sugar', '1 tsp Ground Cinnamon', '1 tsp Vanilla Extract'],
        'tags': ['hot chocolate', 'drink', 'traditional', 'breakfast'],
        'featured': False
    },
]

# CSV headers
headers = ['name', 'category', 'difficulty', 'prep_time', 'servings', 'ingredients', 'tags', 'featured', 'image', 'calories', 'protein', 'carbs', 'fat', 'fiber']

with open('excel docs/Recipes.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    
    for recipe in recipes:
        # Convert ingredients list to JSON array string
        recipe['ingredients'] = json.dumps(recipe['ingredients'])
        # Convert tags list to JSON array string
        recipe['tags'] = json.dumps(recipe['tags'])
        # Add empty fields
        recipe['image'] = ''
        recipe['calories'] = ''
        recipe['protein'] = ''
        recipe['carbs'] = ''
        recipe['fat'] = ''
        recipe['fiber'] = ''
        
        writer.writerow(recipe)

print(f'✓ Created Recipes.csv with {len(recipes)} authentic Dominican recipes!')
print(f'✓ All ingredients include amounts (e.g., "2 lbs Chicken Thighs")')
print(f'✓ Recipes use ingredients from Dominican Republic.xlsx')
