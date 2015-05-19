<!DOCTYPE html>

<html>
<%
response.setHeader("Cache-Control","no-cache"); //HTTP 1.1
response.setHeader("Pragma","no-cache"); //HTTP 1.0
response.setDateHeader ("Expires", 0); //prevents caching at the proxy server
response.sendRedirect("http://"+request.getLocalAddr()+"/login.jsp");
%>
<head>
         <title>Network Authentication Required</title>
      </head>
      <body>
         <p>You need to <a href="http://<%= request.getLocalAddr() %>/login.jsp">
         authenticate with the local network</a> in order to gain
         access.</p>
      </body>
   </html>
