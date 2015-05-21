

import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.net.URLDecoder;
import java.net.URLEncoder;
import java.util.Properties;
import java.util.concurrent.ConcurrentHashMap;

import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.RequestDispatcher;
import javax.servlet.ServletContext;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;


/**
 * Servlet Filter implementation class LoginFilter
 */
public class LoginFilter implements Filter {

    /**
     * Default constructor. 
     */
    public LoginFilter() {
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see Filter#destroy()
	 */
	public void destroy() {
		// TODO Auto-generated method stub
	}

	/**
	 * @see Filter#doFilter(ServletRequest, ServletResponse, FilterChain)
	 */
	public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
		   boolean authorized = false;
		   String requested_path = null;
		   System.out.println("doFilter");
		   if (request instanceof HttpServletRequest) 
		   {
			   
			   if (((HttpServletRequest) request).getRequestURI().matches("(.*?)\\.(js|css)$"))
			    {		    	
			        chain.doFilter(request, response); // Just continue chain.
			        return;
			    }
			   	
			    
			   
		    	HttpSession session = ((HttpServletRequest)request).getSession();
		    	ServletContext sc = session.getServletContext();
		    	
			    String token = ((HttpServletRequest) request).getHeader("X-Auth-Token");
			    if (token != null)
			    {
				    ConcurrentHashMap<String,Long> chm = (ConcurrentHashMap<String,Long>)sc.getAttribute("logged_users");
				    Long token_creation_timestamp = chm.get(token); 
				    
				    /********************************************************************
				    *		   WARNING: Session expires after 5 minutes					*
				    *********************************************************************/
				    if ((token_creation_timestamp!=null)&&((System.currentTimeMillis()-token_creation_timestamp.longValue()) < 60000 * 5))
				    {
						//already authenticated
					    authorized = true;
					    session.setAttribute("token", token);
				    }
			    }
			    else
			    {
			    	
			    	if (((String)sc.getAttribute("captive_portal_ip")).equals(((HttpServletRequest) request).getServerName()) || ((String)sc.getAttribute("captive_portal_ip_external")).equals(((HttpServletRequest) request).getServerName()))
			    	{		
			    		//the user's request is for the captive portal
			    		token = (String) session.getAttribute("token");
			    		
	
						if (token != null)
							//already authenticated
						    authorized = true;
						
						if (session.getAttribute("requested_path") == null)
						{
							String target = ((HttpServletRequest) request).getParameter("target");
							if (target != null)
							{
								//save the requested path inside the session
								session.setAttribute("requested_path", URLDecoder.decode(target,"UTF-8"));
								System.out.println("Set 1 " + URLDecoder.decode(((HttpServletRequest) request).getParameter("target"),"UTF-8"));
							}
						}
					}
			    	else
			    	{
			    		//the user's request is for another host, then I send a redirect on the CapPortal host
			    		
			    		requested_path = "http://"+((HttpServletRequest) request).getServerName()+((HttpServletRequest) request).getRequestURI();
						//requested_path = ((HttpServletRequest) request).getRequestURI();
						System.out.println("Set 2.2 " + requested_path);
						((HttpServletResponse) response).setStatus(HttpServletResponse.SC_TEMPORARY_REDIRECT);
						URL temp = new URL("http",(String)sc.getAttribute("captive_portal_ip"),80,"/Index");
						((HttpServletResponse) response).setHeader("Location", temp.toString()+"?target="+URLEncoder.encode(requested_path,"UTF-8"));

						((HttpServletResponse) response).setHeader("Connection","close");
			    	}
			    }
			    if (authorized) 
			    {
		    		requested_path = "http://"+((HttpServletRequest) request).getServerName()+((HttpServletRequest) request).getRequestURI();
					//requested_path = ((HttpServletRequest) request).getRequestURI();
					System.out.println("Set 2.3" + requested_path);
			    	//the user is already authenticated: continue the filter chain
			        chain.doFilter(request, response);
			        return;
			    }
			    else
			    {
			    	//the user is not authenticated
				    String path = ((HttpServletRequest) request).getRequestURI();
				    if (path.equals("/Login"))
				    {		    	
				        chain.doFilter(request, response); // Just continue chain.
				        return;
				    }
				    else 
				    {	
				    	//redirect him to the Login page
				    	RequestDispatcher dispatch = request.getRequestDispatcher("/login.jsp");       	
						dispatch.forward(request, response);
			        	return;
				    }
	
			    }
		   }

	}

	/**
	 * @see Filter#init(FilterConfig)
	 */
	public void init(FilterConfig fConfig) throws ServletException {

		InputStream input = fConfig.getServletContext().getResourceAsStream("/WEB-INF"+"/captive_portal.properties");
		Properties p = new Properties();
		try {
			p.load(input);
		} catch (IOException e) {
			e.printStackTrace();
			throw new RuntimeException("We encounter an unhandable problem in the request processing. Contact the system administrator.");
		}
		ServletContext sc = fConfig.getServletContext();
        if (sc != null) {
        	
        	// Loads configuration
			sc.setAttribute("captive_portal_ip", p.getProperty("captive_portal_ip"));
			sc.setAttribute("captive_portal_ip_external", p.getProperty("captive_portal_ip_external"));
			sc.setAttribute("keystone_ip", p.getProperty("keystone_ip"));
			sc.setAttribute("keystone_port", p.getProperty("keystone_port"));
			sc.setAttribute("controller_ip", p.getProperty("controller_ip"));
			sc.setAttribute("controller_port", p.getProperty("controller_port"));
			sc.setAttribute("orchestrator_ip", p.getProperty("orchestrator_ip"));//"http://130.192.225.245:8000/orchestrator"
			sc.setAttribute("orchestrator_port", p.getProperty("orchestrator_port"));
			
			//TODO: Start a thread that periodically controls the map and purge the expired entries
			ConcurrentHashMap<String,Long> chm = new ConcurrentHashMap<String,Long>();
			sc.setAttribute("logged_users", chm);
			
			// Generates unique session identifier
			SessionIdentifierGenerator s = new SessionIdentifierGenerator();
			sc.setAttribute("token_generator", s);
        }
		
		
	}

}
