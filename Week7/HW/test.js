const test = async () => {
  try {
    const resPOST = await fetch('http://localhost:8080/api/products', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'Mouse', price: 10.99, category: 'Electronics', stock: 10 })
    });
    const resPOSTText = await resPOST.text();
    console.log("POST Result:", resPOSTText);
    
    const resGET = await fetch('http://localhost:8080/api/products');
    const resGETText = await resGET.text();
    console.log("GET Result:", resGETText);
  } catch (err) {
    console.error(err);
  }
};
test();
