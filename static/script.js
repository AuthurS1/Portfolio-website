function sendMessage(event) {
  event.preventDefault();
  const name = document.getElementById("name").value;
  const email = document.getElementById("email").value;
  const message = document.getElementById("message").value;

  document.getElementById("contact-result").innerText =
    `Cảm ơn ${name}! Tin nhắn của bạn đã được ghi lại (demo).`;
    
  event.target.reset();
}
