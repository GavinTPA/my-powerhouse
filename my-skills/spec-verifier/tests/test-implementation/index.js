// Test implementation - exports main function

function main() {
  try {
    console.log("Running main function");
    processData();
  } catch (error) {
    console.error("Error in main:", error);
  }
}

// Note: This function has NO error handling (intentional for test)
function processData() {
  const data = getData();
  return data.map(item => item.value);
}

// Note: This function has NO error handling (intentional for test)
function getData() {
  return [
    { value: 1 },
    { value: 2 },
    { value: 3 }
  ];
}

module.exports = { main };
