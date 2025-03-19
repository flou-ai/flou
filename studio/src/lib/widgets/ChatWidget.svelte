<script lang="ts">
  import { formatDate } from '$lib/utils';
  
  export let widget: any;
  export let data: any;
  
  // Extract field names from widget configuration
  const { userField = 'user', contentField = 'content', 
          avatarField = null, timestampField = 'timestamp', title = 'Chat' } = widget;
  
  // Ensure data is an array
  $: messages = Array.isArray(data) ? data : [];
</script>

<div class="chat-widget">
  <h3>{title}</h3>
  
  <div class="messages">
    {#if messages.length === 0}
      <div class="no-messages">No messages yet</div>
    {:else}
      {#each messages as message}
        <div class="message {message[userField] === 'user' ? 'user' : 'assistant'}">
          {#if avatarField && message[avatarField]}
            <div class="avatar">
              <img src={message[avatarField]} alt={message[userField]} />
            </div>
          {:else}
            <div class="avatar default-avatar">
              {message[userField]?.charAt(0).toUpperCase() || '?'}
            </div>
          {/if}
          
          <div class="content">
            <div class="header">
              <span class="username">{message[userField]}</span>
              {#if timestampField && message[timestampField]}
                <span class="timestamp">{formatDate(message[timestampField])}</span>
              {/if}
            </div>
            <div class="message-text">{message[contentField]}</div>
          </div>
        </div>
      {/each}
    {/if}
  </div>
</div>

<style>
  .chat-widget {
    background: var(--white);
    border-radius: 0.5rem;
    overflow: hidden;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  h3 {
    margin: 0;
    padding: 1rem;
    border-bottom: 1px solid var(--gray-200);
  }
  
  .messages {
    padding: 1rem;
    overflow-y: auto;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .no-messages {
    color: var(--gray-400);
    text-align: center;
    padding: 2rem;
  }
  
  .message {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 1rem;
  }
  
  .avatar {
    flex-shrink: 0;
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 50%;
    background: var(--gray-200);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    color: var(--gray-700);
  }
  
  .avatar img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
  }
  
  .user .avatar {
    background: var(--blue-100);
    color: var(--blue-700);
  }
  
  .assistant .avatar {
    background: var(--green-100);
    color: var(--green-700);
  }
  
  .content {
    flex-grow: 1;
  }
  
  .header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.25rem;
  }
  
  .username {
    font-weight: bold;
  }
  
  .timestamp {
    font-size: 0.75rem;
    color: var(--gray-500);
  }
  
  .message-text {
    white-space: pre-wrap;
  }
</style>