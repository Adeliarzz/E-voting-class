module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",   // Ganache GUI host
      port: 7545,          // Ganache GUI default port (cek Ganache mu)
      network_id: "*"      // match any network id
    }
  },

  mocha: {
    // timeout: 100000
  },

  compilers: {
    solc: {
      version: "0.8.19",   // versi solc yang akan di-download oleh Truffle
      settings: {
        optimizer: {
          enabled: true,
          runs: 200
        }
      }
    }
  }
};