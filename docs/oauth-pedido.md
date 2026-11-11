# Pedido de login oficial (OAuth) à GGG

Para o app "Meu Baú" deixar de usar o POESESSID, a GGG precisa registrar um **cliente OAuth público** (public client).
Pela documentação da GGG, apps executáveis que rodam fora do jogo devem usar um cliente público, com PKCE e endereço
de retorno local. Isso cabe direto no `bau.exe`, sem servidor.

**Como enviar:** mande o e-mail abaixo, do seu e-mail, para **oauth@grindinggear.com** (não é o e-mail do suporte).
A GGG decide caso a caso e pode demorar semanas. Peça só o escopo necessário.

---

**Assunto:** OAuth public client request – "PoE Builds – Meu Baú" (stash value viewer)

Hello,

I would like to register a public OAuth client for a small open-source desktop tool.

- **Application name:** PoE Builds – Meu Baú
- **Account:** Hygopenido#4999
- **Client type:** Public (Authorization Code with PKCE)
- **Scope requested:** `account:stashes` (read only)
- **Redirect URI:** `http://127.0.0.1:7373/oauth/callback`
- **Source code:** https://github.com/Jantare/poe-builds/tree/main/bau
- **Website:** https://jantare.github.io/poe-builds/bau/

**What it does:** the user runs the app on their own Windows PC. It opens a local page in their browser, reads the
stash tabs they choose, prices the items with poe.ninja's public economy data, and shows the total value per tab and a
history between farming sessions. All data stays on the user's computer; there is no server and nothing is shared.

**Request volume:** only when the user clicks "Update", one request per selected tab, respecting the
`X-Rate-Limit-*` headers and `Retry-After`. The app sends an identifiable User-Agent with a contact address.

Today the tool asks users for their POESESSID, which we would like to stop doing for security reasons.

Thank you!

---

Quando a GGG responder com o `client_id`, me passe o número (ele não é segredo num cliente público) para eu ligar o
botão "Entrar com Path of Exile" no app.
