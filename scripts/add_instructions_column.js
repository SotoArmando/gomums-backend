const fs = require('fs');
const path = require('path');

// Add instructions column to CSV files
function addInstructionsColumn(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n');
  
  const updatedLines = lines.map((line, index) => {
    if (!line.trim()) return line;
    
    // Skip if line already has instructions
    if (line.includes('"[""Season all meats') || 
        line.includes('"[""Cook beans:') || 
        line.includes('"[""Drain pigeon peas') || 
        line.includes('"[""Cut chicken into pieces') || 
        line.includes('"[""Peel and cut plantains') ||
        line.includes('"[""Preheat oven to') ||
        line.includes('"[""Bring a large pot') ||
        line.includes('"[""Cook rice according') ||
        line.includes('"[""Cut chicken into bite') ||
        line.includes('"[""Pat chicken dry') ||
        line.includes('instructions') ||
        line.endsWith(',"[]"')) {
      return line;
    }
    
    // Add empty instructions array
    return line + ',"[]"';
  });
  
  fs.writeFileSync(filePath, updatedLines.join('\n'), 'utf-8');
  console.log(`✅ Updated ${filePath}`);
}

// Process Kansas file
const kansasPath = path.join(__dirname, '../excel docs/Recipes Kansas.csv');
addInstructionsColumn(kansasPath);
console.log('Kansas recipes updated!');
