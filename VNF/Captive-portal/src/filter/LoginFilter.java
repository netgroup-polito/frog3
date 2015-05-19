/************************************************************************************
*																					*
*     Copyright notice: please read file license.txt in the project root folder.    *
*                                              								     	*
************************************************************************************/

package filter;

import java.io.IOException;
import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;



/**
 * Servlet Filter implementation class LoginFilter
 */
public class LoginFilter implements Filter {

	/**
	 * Default constructor. 
	 */
	public LoginFilter() {
	}

	/**
	 * @see Filter#destroy()
	 */
	public void destroy() {
	
	}

	/**
	 * @see Filter#doFilter(ServletRequest, ServletResponse, FilterChain)
	 */
	public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
		System.out.println("Login Filter executed");
		HttpServletRequest request2 = (HttpServletRequest) request;
		
		String ipAddress=request.getRemoteAddr();
		//String web_port= "10"+ipAddress.substring(ipAddress.lastIndexOf(".")+1, ipAddress.length());
		
		if(request2.getSession().getAttribute("user") == null || request2.getSession().getAttribute("user").equals(""))// || ca.RunCheckAlive(web_port))
		{
			request2.getServletContext().getRequestDispatcher("/index.jsp").forward(request, response);
			return;
		}

		chain.doFilter(request, response);
	}

	/**
	 * @see Filter#init(FilterConfig)
	 */
	public void init(FilterConfig fConfig) throws ServletException {

	}

}
