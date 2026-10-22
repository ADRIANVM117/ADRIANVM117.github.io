```{=html}
<div class="research-listing list">
<% const typeLabels = { project: 'Proyecto de investigación', note: 'Nota de investigación', journal: 'Diario de investigación' }; %>
<% const statusLabels = { ongoing: 'En curso', completed: 'Completada', archived: 'Archivada' }; %>
<% if (items.length === 0) { %>
<div class="research-empty">
  <p class="micro">EN DESARROLLO</p>
  <p>Las investigaciones aparecerán aquí cuando estén listas para compartirse.</p>
</div>
<% } %>
<% for (const item of items) { %>
<article class="research-entry" <%= metadataAttrs(item) %>>
  <div>
    <div class="micro research-entry-meta">
      <% if (item.type) { %><span><%= typeLabels[item.type] || item.type %></span><% } %>
      <% if (item.status) { %><span>·</span><span><%= statusLabels[item.status] || item.status %></span><% } %>
    </div>
    <h2><a href="<%- item.path %>" class="no-external"><%= item.title %></a></h2>
    <% if (item.description) { %><p><%= item.description %></p><% } %>
  </div>
  <div class="research-entry-aside">
    <% if (item.date) { %><div class="micro research-entry-date"><%= item.date %></div><% } %>
    <% if (item.topics && item.topics.length) { %><div class="research-topic-list"><% for (const topic of item.topics) { %><span class="research-topic"><%= topic %></span><% } %></div><% } %>
    <a class="research-entry-link no-external" href="<%- item.path %>">Leer investigación ↗</a>
  </div>
</article>
<% } %>
</div>
```
