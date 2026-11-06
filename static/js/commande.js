// Estimation du total au tarif normal pendant la saisie.
// Ce calcul est seulement indicatif : le vrai prix (avec réduction)
// est calculé par le serveur Python à partir des prix en base.
(function () {
  const champs = document.querySelectorAll(".quantite");
  const sortie = document.getElementById("estimation");
  if (!sortie) return;

  function formater(montant) {
    return Math.round(montant).toLocaleString("fr-FR") + " FCFA";
  }

  function recalculer() {
    let total = 0;
    champs.forEach((champ) => {
      const quantite = parseInt(champ.value, 10) || 0;
      total += quantite * parseFloat(champ.dataset.prix);
    });
    sortie.textContent = formater(total);
  }

  champs.forEach((champ) => champ.addEventListener("input", recalculer));
  recalculer();
})();
