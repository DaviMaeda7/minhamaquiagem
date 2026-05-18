export async function onRequestPost({ request, env }) {
  const { email, password } = await request.json();

  // substitua pelas credenciais reais
  const EMAIL_CERTO = 'davimaeda@gmail.com';
  const SENHA_CERTA = 'suasenha';

  if (email === EMAIL_CERTO && password === SENHA_CERTA) {
    return Response.json({ success: true });
  }

  return Response.json(
    { success: false, message: 'E-mail ou senha incorretos.' },
    { status: 401 }
  );
}