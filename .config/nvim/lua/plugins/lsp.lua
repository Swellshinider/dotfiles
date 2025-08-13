return {
  "neovim/nvim-lspconfig",
  dependencies = {
    "williamboman/mason.nvim",
    "williamboman/mason-lspconfig.nvim",
  },
  config = function()
    require("mason").setup()
    require("mason-lspconfig").setup({
      ensure_installed = { "omnisharp", "lua_ls" },
    })

    local lspconfig = require("lspconfig")
    local caps = require("cmp_nvim_lsp").default_capabilities()

    lspconfig.omnisharp.setup({
      capabilities = caps,
      -- root dir for .NET projects
      root_dir = lspconfig.util.root_pattern("*.sln", "*.csproj", ".git"),
    })

    lspconfig.lua_ls.setup({
      capabilities = caps,
      settings = { Lua = { diagnostics = { globals = { "vim" } } } },
    })
  end,
}

