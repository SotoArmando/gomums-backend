const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'gomums',
  user: 'postgres',
  password: '7646'
});

async function checkHomeSections() {
  try {
    console.log('\n='.repeat(70));
    console.log('Checking Home Sections');
    console.log('='.repeat(70));
    
    const result = await pool.query(`
      SELECT 
        id,
        type,
        title,
        subtitle,
        user_id,
        visible,
        order_index,
        data
      FROM home_sections
      WHERE title ILIKE '%week%' OR title ILIKE '%recipe%'
      ORDER BY order_index
    `);
    
    if (result.rows.length === 0) {
      console.log('\n❌ No sections found matching "week" or "recipe"\n');
      
      // Show all sections
      const allSections = await pool.query(`
        SELECT id, type, title, subtitle, visible, order_index, data
        FROM home_sections
        ORDER BY order_index
      `);
      
      console.log('\n📋 All Home Sections:');
      console.log('-'.repeat(70));
      allSections.rows.forEach(section => {
        console.log(`\n${section.visible ? '✅' : '❌'} ${section.title}`);
        console.log(`   Type: ${section.type}`);
        console.log(`   Subtitle: ${section.subtitle}`);
        console.log(`   Order: ${section.order_index}`);
        console.log(`   Data:`, JSON.stringify(section.data, null, 2));
      });
    } else {
      console.log(`\n✅ Found ${result.rows.length} section(s):\n`);
      
      result.rows.forEach(section => {
        console.log('-'.repeat(70));
        console.log(`📌 ${section.title}`);
        console.log(`   Type: ${section.type}`);
        console.log(`   Subtitle: ${section.subtitle || 'N/A'}`);
        console.log(`   User ID: ${section.user_id || 'GLOBAL'}`);
        console.log(`   Visible: ${section.visible ? 'Yes' : 'No'}`);
        console.log(`   Order: ${section.order_index}`);
        console.log(`   Data:`, JSON.stringify(section.data, null, 2));
      });
    }
    
    console.log('\n' + '='.repeat(70) + '\n');
    
  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await pool.end();
  }
}

checkHomeSections();
