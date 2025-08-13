vim.o.number = true
vim.g.mapleader = " "

require("swell.lazy")

-- Treat .axaml as XML (Avalonia)
vim.filetype.add({ extension = { axaml = "xml" } })
