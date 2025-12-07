const phantomPayBtn = document.getElementById("phantom-pay");
phantomPayBtn.onclick = async () => {
  if (!window.solana || !window.solana.isPhantom) {
    alert("Please install Phantom wallet");
    return;
  }
  await window.solana.connect();
  const provider = window.solana;
  const connection = new solanaWeb3.Connection(
    "https://api.mainnet-beta.solana.com"
  );
  const from = new solanaWeb3.PublicKey(provider.publicKey.toString());
  const to = new solanaWeb3.PublicKey("YOUR_USDC_ADDRESS"); // replace with your USDC address
  const amount = 99 * 1_000_000; // 99 USDC (6 decimals)

  const tx = new solanaWeb3.Transaction().add(
    solanaWeb3.createTransferInstruction(from, to, amount)
  );

  const { blockhash } = await connection.getLatestBlockhash();
  tx.recentBlockhash = blockhash;
  tx.feePayer = from;

  const signed = await provider.signTransaction(tx);
  const txid = await connection.sendRawTransaction(signed.serialize());
  await connection.confirmTransaction(txid);

  // tell backend
  const res = await fetch("/crypto/capture", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tx_signature: txid, amount_usd: 99 }),
  });
  const data = await res.json();
  if (data.success) window.location = "/dashboard?success=1";
  else alert(data.error);
};
