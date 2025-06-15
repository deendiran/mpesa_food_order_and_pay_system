-- SQLite

-- INSERT INTO categories (id, name, description, image_url, is_active, created_at)
-- VALUES 
-- (1, 'Drinks', 'Refreshing beverages', 'https://thumbs.dreamstime.com/b/cans-beverages-19492376.jpg?w=768', 1, NULL),
-- (2, 'Desserts', 'Sweet treats to finish your meal', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ2w_lMYEi3T0kn4WXP6i4C_6FqeWeNaVeXfA&s', 1, NULL),
-- (3, 'Pizza', 'Delicious pizzas with different toppings', 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Pizza-3007395.jpg/1200px-Pizza-3007395.jpg', 1, NULL),
-- (4, 'Burgers', 'Juicy burgers with various toppings', 'https://www.foodandwine.com/thmb/jldKZBYIoXJWXodRE9ut87K8Mag=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/crispy-comte-cheesburgers-FT-RECIPE0921-6166c6552b7148e8a8561f7765ddf20b.jpg', 1, NULL),
-- (5, 'Chicken', 'Crispy fried chicken and grilled specialties', 'https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?w=400', 1, '2025-06-08 10:15:31'),
-- (6, 'Pasta', 'Fresh pasta dishes with rich sauces', 'https://www.spicebangla.com/wp-content/uploads/2024/08/Spicy-Pasta-recipe-optimised-scaled.webp', 1, '2025-06-08 10:16:14');


-- INSERT INTO menu_items (id, name, description, price, image_url, category_id, is_available)
-- VALUES 
-- (1, 'Orange juice', 'Healthy orange juice', 100.0, 'https://www.saberhealth.com/uploaded/blog/images/orange-juice.jpg', 1, 1),
-- (2, 'Chocolate cake', 'Delicious chocolate cake', 150.0, 'https://scientificallysweet.com/wp-content/uploads/2023/06/IMG_4087-er-new1.jpg', 2, 1),
-- (4, 'Hawaiian', '', 1200.0, 'https://www.allrecipes.com/thmb/xYu9Ii8paEyMcJy7sv2mYxwfd7Q=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/hawaiian-pizza-ddmfs-3x2-132-450eff04ad924d9a9eae98ca44e3f988.jpg', 3, 1),
-- (5, 'Chocolate', '', 130.0, 'https://scientificallysweet.com/wp-content/uploads/2023/06/IMG_4087-er-new1.jpg', 2, 1),
-- (6, 'Classic Beef Burger', 'Juicy beef patty with lettuce, tomato, onion, and our special sauce', 850.0, 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400', 4, 1),
-- (7, 'Chicken Deluxe Burger', 'Grilled chicken breast with bacon, cheese, and avocado', 950.0, 'https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=400', 4, 1),
-- (8, 'Pepperoni Pizza', 'Traditional pepperoni with mozzarella cheese', 1400.0, 'https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400', 3, 1),
-- (9, 'BBQ Chicken Pizza', 'Grilled chicken with BBQ sauce, red onions, and cilantro', 1600.0, 'https://www.allrecipes.com/thmb/wSqQsq5SC-wy_7Ys7RkYJdDWwTo=/0x512/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/AR-24878-bbq-chicken-pizza-beauty-4x3-39cd80585ad04941914dca4bd82eae3d.jpg', 3, 1),
-- (10, 'Margherita Pizza', 'Classic pizza with tomato sauce, mozzarella, and fresh basil', 1200.0, 'https://cdn.loveandlemons.com/wp-content/uploads/2023/07/margherita-pizza-recipe.jpg', 3, 1),
-- (11, 'Iced Coffee', 'Cold brew coffee with milk and sugar', 300.0, 'https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400', 1, 1),
-- (12, 'Strawberry Smoothie', 'Creamy strawberry smoothie with yogurt', 350.0, 'https://images.unsplash.com/photo-1553530666-ba11a7da3888?w=400', 1, 1),
-- (13, 'Vanilla Ice Cream', 'Premium vanilla ice cream with toppings', 250.0, 'https://www.allrecipes.com/thmb/bTcUVF3wiDRXkY0HQvQgpStGMlY=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/AR-8314-Vanilla-Ice-Cream-gw-ddmfs-beauty-4x3-b0f065ec1e7346abb82f4b3d2ad9907b.jpg', 2, 1),
-- (14, 'Apple Pie', 'Homemade apple pie with cinnamon', 400.0, 'https://www.southernliving.com/thmb/6FtLB2jOC-9nvdHDlwd5IITtV9k=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/2589601_Mailb_Mailbox_Apple_Pie_003-da802ff7a8984b2fa9aa0535997ab246.jpg', 2, 1),
-- (15, 'Spaghetti Carbonara', 'Classic Italian pasta with eggs, cheese, and pancetta', 950.0, 'https://www.recipetineats.com/tachyon/2023/01/Carbonara_6a.jpg?resize=900%2C1125&zoom=0.86', 6, 1),
-- (16, 'Chicken Alfredo', 'Fettuccine pasta with grilled chicken in creamy alfredo sauce', 1100.0, 'https://bellyfull.net/wp-content/uploads/2021/02/Chicken-Alfredo-blog-4-1152x1536.jpg', 6, 1),
-- (17, 'Penne Arrabbiata', 'Spicy tomato sauce with garlic and red peppers', 850.0, 'https://tastesbetterfromscratch.com/wp-content/uploads/2020/03/Penne-Arrabbiata-1-2.jpg', 6, 1),
-- (18, 'Crispy Chicken Wings', '8 pieces of crispy wings with your choice of sauce', 700.0, 'https://cdn.apartmenttherapy.info/image/upload/f_auto,q_auto:eco,c_fill,g_auto,w_610,h_458/k%2FPhoto%2FRecipe%20Ramp%20Up%2F2022-02-Baked-Chicken-Wings%2FIMG_6923_f6aa7e_landscape', 5, 1),
-- (19, 'Grilled Chicken Breast', 'Seasoned grilled chicken breast with herbs', 800.0, 'https://hips.hearstapps.com/hmg-prod/images/grilled-chicken-breast-lead-6626cdb0bb5ac.jpg?crop=1xw:1xh;center,top&resize=640:*', 5, 1),
-- (20, 'Chicken Tenders', 'Golden fried chicken tenders with mustard', 750.0, 'https://littlesunnykitchen.com/wp-content/uploads/2021/01/Garlic-Butter-Chicken-Tenders-7-1024x1536.jpg', 5, 1);


-- SELECT * FROM menu_items;

-- SELECT * FROM categories;

-- SELECT * FROM users;