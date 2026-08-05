// Example of how your frontend will fetch the database data
async function loadProductsFromNeon() {
  try {
    const response = await fetch('https://your-api-url.com/api/products');
    const dbProducts = await response.json();
    
    // Assign to your existing PRODUCTS variable
    PRODUCTS = dbProducts; 
    
    // Re-render the UI
    renderProducts();
  } catch (error) {
    console.error("Failed to load products from database", error);
  }
}

// Call this on page load
loadProductsFromNeon();

require('dotenv').config();
const { Pool } = require('pg');

const pool = new Pool({
  host: process.env.PGHOST,
  database: process.env.PGDATABASE,
  user: process.env.PGUSER, // <-- use "user", not "username"
  password: process.env.PGPASSWORD,
  port: 5432,
  ssl: {
    rejectUnauthorized: false,
  },
});

async function getPgVersion() {
  try {
    const client = await pool.connect();
    const result = await client.query('SELECT version()');
    console.log(result.rows[0]);
    client.release();
  } catch (err) {
    console.error('Connection error:', err);
  } finally {
    await pool.end();
  }
}

getPgVersion();

