const { generate } = require('youtube-po-token-generator')

generate()
  .then(console.log)  // Logs the visitorData and poToken
  .catch(console.error);  // Logs any errors
