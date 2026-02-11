const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'gomums',
  user: 'postgres',
  password: '7646'
});

async function removeDuplicates() {
  try {
    console.log('\n' + '='.repeat(70));
    console.log('Removing Duplicate Home Sections');
    console.log('='.repeat(70));
    
    // Find all "Step-by-Step Recipes" sections
    const duplicates = await pool.query(`
      SELECT id, title, user_id, created_at
      FROM home_sections
      WHERE title = 'Step-by-Step Recipes'
      ORDER BY created_at ASC
    `);
    
    if (duplicates.rows.length <= 1) {
      console.log('\n✅ No duplicates found!\n');
      await pool.end();
      return;
    }
    
    console.log(`\n📋 Found ${duplicates.rows.length} sections with title "Step-by-Step Recipes"`);
    
    // Keep the first one, delete the rest
    const toKeep = duplicates.rows[0];
    const toDelete = duplicates.rows.slice(1);
    
    console.log(`\n✅ Keeping: ${toKeep.id} (created ${toKeep.created_at})`);
    console.log(`\n🗑️  Deleting ${toDelete.length} duplicate(s):`);
    
    for (const section of toDelete) {
      console.log(`   - ${section.id} (created ${section.created_at})`);
      await pool.query('DELETE FROM home_sections WHERE id = $1', [section.id]);
    }
    
    console.log('\n✨ Duplicates removed successfully!');
    
    // Show remaining sections
    const remaining = await pool.query(`
      SELECT id, type, title, visible, order_index, user_id
      FROM home_sections
      ORDER BY order_index
    `);
    
    console.log('\n📊 Remaining Home Sections:');
    console.log('-'.repeat(70));
    remaining.rows.forEach(section => {
      const scope = section.user_id ? 'User-specific' : 'Global';
      console.log(`${section.visible ? '✅' : '❌'} [${section.order_index}] ${section.title} (${scope})`);
    });
    
    console.log('\n' + '='.repeat(70) + '\n');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await pool.end();
  }
}

removeDuplicates();
