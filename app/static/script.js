const socket = io("http://localhost:8000", {
    query: {
      user_id: user_id_j
    }
  });
  
  socket.on("connect", () => {
    console.log("Connected to server with ID:", socket.id);
    console.log("user_id_j",user_id_j)
  });
  
  // variables
  const messageInput = document.getElementById("msg");
  const contactList = document.getElementById("contact-list");
  const currentUserId = user_id_j;
  let seen_ = null;
  let selectedContact = null;
  let currentSelectedUsername = null;
  let typingTimeout; 
  let typingIndicatorElement = null;
  const sendBtn = document.getElementById("send_msg");


  socket.on("status_online", (data) => {
    console.log("status online", data);
    const statusElement = document.getElementById("status-text");
    statusElement.textContent = "online";
  });

  socket.on("status_offline", (data) => {
    console.log("status offline", data.data);
    const statusElement = document.getElementById("status-text");
    statusElement.textContent = "offline";
  });

    // Deselect previous
  window.addEventListener("beforeunload", () => {
      if (selectedContact) {
        const deselectedUsername = selectedContact.dataset.username;
        const payload = {
          deselected_username: deselectedUsername,
          my_id: currentUserId,
        };
    
        const blob = new Blob([JSON.stringify(payload)], { type: "application/json" });
        navigator.sendBeacon("/chat_deselected", blob);
      }
  });

    // Set up input listener only once
  messageInput.addEventListener("input", (event) => {
      event.preventDefault();
      if (currentSelectedUsername) {
        console.log('typing:', currentSelectedUsername);
        socket.emit("typing", {"username":currentSelectedUsername,"user_id":currentUserId});
      }
  })

  // lastseen function
  function formatLastSeen(lastSeenEpoch) {
    if (lastSeenEpoch === 0) {
        return "Status not available";
    }

    
    const lastSeenDate = new Date(lastSeenEpoch); 
    const now = new Date();
    const diff = now.getTime() - lastSeenDate.getTime();

    
    if (isNaN(lastSeenDate.getTime())) {
        return "Invalid time format";
    }

    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    
    const formatDate = (date) => {
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = String(date.getFullYear()).slice(-2);
        return `${day}/${month}/${year}`;
    };

    if (days === 0) {
        if (minutes < 1) {
            return "Last seen few seconds ago";
        } else if (hours < 1) {
            return `Last seen ${minutes} minutes ago`;
        } else {
            return `Last seen ${hours} hours ago`;
        }
    } else {
        // Use custom formatter instead of toLocaleDateString()
        return `Last seen on ${formatDate(lastSeenDate)}`; 
    }
}
  // fetch lastseen
  async function getLastSeen(username) {
    console.log("async")
    try {
      const response = await fetch(`/get-lastseen/${username}`);
      const data = await response.json();
       // ... status handling code ...
       const statusElement = document.getElementById("status-text");
       statusElement.textContent = data.status === false
        ? formatLastSeen(data.lastseen)
        : (data.status === true ? "online" : "");

    } catch (error) {
      console.error('Error:', error);
    }
  }

  // creates message element
  function createMessageElement(message) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message");
    messageElement.classList.add(message.sender_id === currentUserId ? "sent" : "received");
    if (message.id) {
        messageElement.id = `${message.id}`;
    }

    const messageTextElement = document.createElement("p");
    messageTextElement.textContent = message.message_text;
    messageElement.appendChild(messageTextElement);

    const timestamp = new Date(message.timestamp);
    const formattedTimestamp = timestamp.toLocaleString([], {
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });

    const timestampElement = document.createElement("small");
    timestampElement.textContent = formattedTimestamp;
    messageElement.appendChild(timestampElement);

    const statusElement = document.createElement("small");
    statusElement.textContent = message.seen;
    if (message.seen === "sent") {
        statusElement.id = "sent";
    }
    messageElement.appendChild(statusElement);

    return messageElement;
}
  
  async function fetchChat(username) {
    try {
      const response = await fetch('/get-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, user_id: currentUserId }),
      });
      if (!response.ok) throw new Error(response.statusText);
      const data = await response.json();
  
      const chatMessages = document.querySelector(".chat-messages");
      chatMessages.innerHTML = "";
      const epti = data.ep_ti
      console.log("epti",epti)
      
      data.message_data.forEach((message) => {
        console.log("timstamp",message.timestamp)
        let seene = null;
        if (message.timestamp > epti) {
          seene = "sent";
        }
        if (message.timestamp <= epti || message.sender_id != currentUserId) {
          seene = "✔️✔️";
        }
        const Message = {
          sender_id: message.sender_id,
          message_text: message.message_text,
          timestamp: message.timestamp,
          seen: seene,
        };
        chatMessages.appendChild(createMessageElement(Message));
      });
  
      // sending response to sender for seeing msg
      socket.emit("msf", { su: username, id: currentUserId });
  
      // Scroll to bottom after loading messages
      chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (err) {
      console.error("Chat fetch error:", err);
    }
  }

    document.querySelector('.contacts-container').addEventListener('click', (e) => {
      const contactItem = e.target.closest('.contact-item');
      if (!contactItem) return;
    
      const username = contactItem.dataset.username;
      currentSelectedUsername = username; 

      if (selectedContact === contactItem) return;
    
    // Deselect previous
    if (selectedContact) {
        const prevUsername = selectedContact.dataset.username;  // Get from DOM
        selectedContact.classList.remove('selected');
        document.dispatchEvent(new CustomEvent('chat:deselected', {
          detail: { username: prevUsername }  // Use DOM-stored value
        }));
      }
  
    // Select new
    selectedContact = contactItem;
    selectedContact.classList.add('selected');
    document.dispatchEvent(new CustomEvent('chat:selected', {
      detail: { username }
    }));
  
    // Update topbar name
    const contactName = contactItem.querySelector("div > div:first-child").textContent;
    document.querySelector(".chat-topbar .topbar-name").textContent = contactName;
  
    // fetch lastseen and add it to topbar
    getLastSeen(username);
    
    // Fetch chat messages
    fetchChat(username);
      
    
  });
  
  // Event listeners for custom events
  document.addEventListener('chat:selected', (e) => {
    console.log("selected chat:", e.detail.username);
    socket.emit("chat_selected",{"selected_username":e.detail.username, "my_id":currentUserId } )
  });
  
  document.addEventListener('chat:deselected', (e) => {
    console.log("Deselected chat:", e.detail.username);
    socket.emit("chat_deselected",{"deselected_username":e.detail.username, "my_id":currentUserId, "cct":Date.now() } )
  });

  

  socket.on("typin_indicator", (data) => {
    const chatMessages = document.querySelector(".chat-messages");
  
    // Remove existing typing indicator if any
    if (typingIndicatorElement && typingIndicatorElement.parentNode === chatMessages) {
      chatMessages.removeChild(typingIndicatorElement);
    }
    
  
    // Create new typing indicator element
    typingIndicatorElement = document.createElement("div");
    typingIndicatorElement.classList.add("message", "received", "typing-indicator");
    typingIndicatorElement.textContent = `${data.data || "User"} is typing`;

    chatMessages.appendChild(typingIndicatorElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  
    // Clear previous timeout
    clearTimeout(typingTimeout);
  
    // Remove the typing indicator after 2 seconds
    typingTimeout = setTimeout(() => {
      if (typingIndicatorElement) {
        chatMessages.removeChild(typingIndicatorElement);
        typingIndicatorElement = null;
      }
    }, 2000);
    });

    function formatUTCNow(format) {
      const date = new Date(new Date().toUTCString());
      const map = {
        "%Y": date.getUTCFullYear(),
        "%y": date.getUTCFullYear().toString().slice(-2),
        "%m": (date.getUTCMonth() + 1).toString().padStart(2, '0'),
        "%d": date.getUTCDate().toString().padStart(2, '0'),
        "%H": date.getUTCHours().toString().padStart(2, '0'),
        "%M": date.getUTCMinutes().toString().padStart(2, '0'),
        "%S": date.getUTCSeconds().toString().padStart(2, '0'),
      };
    
      return format.replace(/%[YmdHMSy]/g, match => map[match]);
    }
    
    // helper function for unique id
    function generateUniqueId() {
      return `${Math.floor(100 + Math.random() * 900)}`;
    }


    // Send message handler
    sendBtn.addEventListener("click", () => {
      event.preventDefault();
      console.log("sendbtn");
      const message = messageInput.value.trim();
      if (message && currentSelectedUsername) {

        uuid = generateUniqueId();
      
        const fullMessage = {
          sender_id: currentUserId,
          message_text: message,
          timestamp : Date.now(),
          seen : "sending",
          id: uuid
        };
        const messageElement = createMessageElement(fullMessage);
        const chatMessages = document.querySelector(".chat-messages");
      
        // Remove typing indicator if present
        if (typingIndicatorElement && typingIndicatorElement.parentNode === chatMessages) {
          chatMessages.removeChild(typingIndicatorElement);
          typingIndicatorElement = null;
        }
      
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        socket.emit("client_message", {"message":message, "rec_username":currentSelectedUsername, "uuid":uuid} );
        messageInput.value = "";
      }
  });

  socket.on("msg_reached", (data) => {
    if (currentSelectedUsername == data.ru) {
      const messageElement = document.getElementById(data.uuid);
      if (messageElement) {
        const statusElement = messageElement.querySelector('small:last-child');
        statusElement.textContent = "sent";
        statusElement.id = "sent";
      }
    }
  });
  // message seen reciever
  socket.on("msr", (data) => {
    if (currentSelectedUsername == data.ru) {
      const messageElement = document.getElementById(data.uuid);
      if (messageElement) {
        const statusElement = messageElement.querySelector('small:last-child');
        statusElement.textContent = "✔️✔️";
        statusElement.removeAttribute('id');
      }
    }
  });
  // ack message seen
  socket.on("ams", (data) => {
    console.log("ams",data.ru)
    if (currentSelectedUsername == data.ru){
      const sentElements = document.querySelectorAll('#sent');
      sentElements.forEach(element => {
        element.textContent = '✔️✔️';
      });
    }
  });

  // Receive message handler
  socket.on("server_response", (data) => {
    console.log("data.ru",data.su)
    console.log("currentusername",currentSelectedUsername)
    if(currentSelectedUsername == data.su){
        const message = data;
        // Defensive check
        if (!message || !message.data || !message.sender_id) {
          console.error("Malformed message:", message);
          return;
        }
        
          const fullMessage = {
            sender_id: message.sender_id,
            message_text: message.data,
            timestamp : message.timestamp,
            seen : '✔️✔️'
          };
          const messageElement = createMessageElement(fullMessage);
        
         socket.emit("msg_seen",{"uuid": data.uuid, "su":data.su, "ri":currentUserId });

        const chatMessages = document.querySelector(".chat-messages");
      
        // Remove typing indicator if present
        if (typingIndicatorElement && typingIndicatorElement.parentNode === chatMessages) {
          chatMessages.removeChild(typingIndicatorElement);
          typingIndicatorElement = null;
        }
      
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
      }
  });
  // function for create contact elemnent in realtime
  function createContactElement(cont_name,cont_username) {
    const contactItem = document.createElement("div");
    contactItem.className = "contact-item";
    contactItem.dataset.username = cont_username;
  
    const img = document.createElement("img");
    img.src = "https://i.pravatar.cc/40?img=1";
  
    const contactInfo = document.createElement("div");
  
    const c_name = document.createElement("div");
    c_name.style.fontWeight = "600";
    c_name.textContent = cont_name;
  
    const c_username = document.createElement("div");
    c_username.className = "user-status";
    c_username.textContent = cont_username;
  
    contactInfo.appendChild(c_name);
    contactInfo.appendChild(c_username);
  
    contactItem.appendChild(img);
    contactItem.appendChild(contactInfo);
  
    return contactItem;
  }
  // create contact elemnent in realtime
  socket.on("adc", (data) => {
        const contactList = document.getElementById("contact-list");
        if (contactList) {
            const newContact = createContactElement("Not Saved", data.cu);
            contactList.appendChild(newContact);
        } else {
            console.error("Contact list container not found");
        }
        });