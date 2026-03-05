--[[
Valide les contrats statiques des mini-jeux CursedWare.
Parametres:
  arg[1..n]: liste de fichiers game.lua a verifier
Retour:
  code 0 si tous les contrats sont valides, 1 sinon
]]

local motifs_requis = {
    { nom = "module.Name", motif = 'module%.Name%s*=%s*"[^"]+"' },
    { nom = "module.IsActive", motif = "module%.IsActive%s*=%s*true", motif_alternatif = "module%.IsActive%s*=%s*false" },
    { nom = "module.new", motif = "function%s+module%.new%s*%(" },
    { nom = "module:GetObjective", motif = "function%s+module:GetObjective%s*%(" },
    { nom = "module:GetTime", motif = "function%s+module:GetTime%s*%(" },
    { nom = "module:getObjective", motif = "function%s+module:getObjective%s*%(" },
    { nom = "module:setObjective", motif = "function%s+module:setObjective%s*%(" },
    { nom = "module:Setup", motif = "function%s+module:Setup%s*%(" },
    { nom = "module:Start", motif = "function%s+module:Start%s*%(" },
    { nom = "module:Update", motif = "function%s+module:Update%s*%(" },
    { nom = "module:Stop", motif = "function%s+module:Stop%s*%(" },
    { nom = "module:Cleanup", motif = "function%s+module:Cleanup%s*%(" },
    { nom = "return module", motif = "return%s+module" },
}

-- Charge le contenu texte d un fichier.
local function lire_fichier(chemin)
    local fichier = assert(io.open(chemin, "r"))
    local contenu = fichier:read("*a")
    fichier:close()
    return contenu
end

-- Verifie un point d entree mini-jeu.
local function verifier_fichier(chemin)
    local chargeur, erreur = loadfile(chemin)
    if not chargeur then
        io.stderr:write("ERREUR CursedWare: syntaxe invalide dans " .. chemin .. " : " .. erreur .. "\n")
        return false
    end

    local contenu = lire_fichier(chemin)
    for _, definition in ipairs(motifs_requis) do
        local motif_valide = contenu:match(definition.motif)
        if not motif_valide and definition.motif_alternatif then
            motif_valide = contenu:match(definition.motif_alternatif)
        end

        if not motif_valide then
            io.stderr:write(
                "ERREUR CursedWare: contrat mini-jeu incomplet dans "
                .. chemin
                .. " : "
                .. definition.nom
                .. " manquant.\n"
            )
            return false
        end
    end

    return true
end

-- Point d entree principal.
local function main()
    if #arg == 0 then
        io.stderr:write("ERREUR CursedWare: aucun fichier game.lua fourni au validateur.\n")
        os.exit(1)
    end

    for _, chemin in ipairs(arg) do
        if not verifier_fichier(chemin) then
            os.exit(1)
        end
    end

    io.write("OK CursedWare : ", #arg, " mini-jeu(x) valides\n")
end

main()
