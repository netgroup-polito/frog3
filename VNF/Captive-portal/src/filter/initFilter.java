/************************************************************************************
 *																					*
 *     Copyright notice: please read file license.txt in the project root folder.   *
 *                                              								    *
 ************************************************************************************/

package filter;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.Date;
import java.util.Timer;

import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;




/**
 * Servlet Filter implementation class initFilter
 */
public class initFilter implements Filter {

	//private SessionFactory factory;
	private Timer CleanDB;
	private Timer CheckUsers;
	private Timer CheckTempUsers;
	private Timer CheckMgmt;
	private static final String[] browser_id =  { "Chrome", "Firefox", "Safari", "Opera", "MSIE 8", "MSIE 7", "MSIE 6" };
	/**
	 * Default constructor. 
	 */
	public initFilter() {

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

		/**
		 * DA SCOMMENTARE
		 

		if(!request.getServerName().equals("goto.myfrog"))
		{

			String userAgent = ((HttpServletRequest) request).getHeader("User-Agent");
			System.out.println(userAgent);
			for(String b : browser_id)
			{
				if(userAgent.contains(b))
				{
					System.out.println("----->"+ request.getRemoteAddr()+" has searched "+ request.getServerName());
					IPtoURL.getInstance().put(request.getRemoteAddr(), request.getServerName());
				}
			}

			HttpServletResponse r = (HttpServletResponse) response;

			r.setHeader("Cache-Control", "no-cache");
			r.setHeader("Cache-Control", "no-store");
			r.setHeader("Pragma", "no-cache");
			r.setDateHeader("Expires", -1);
			r.setStatus(200);
			//r.setHeader("Location", "http://goto.myfrog/");
			r.setHeader("Connection", "close");
			r.getOutputStream().write("<html><head><meta http-equiv=\"refresh\" content=\"0; url=http://goto.myfrog/\"></head></html>".getBytes());

			//			r.sendRedirect("http://goto.myfrog/");
			return;
		}

*/
		//Transaction tx =null;
		//Session s = factory.getCurrentSession();
		try {
			
			//tx=s.beginTransaction();

			//request.setAttribute("Session", s);

			// FULVIO 3/11/2013
			// Are you sure that it's better to use this code, with such a long path embedded?
			// I saw in other portions of the server a much cleaner way to get it:
			// String ConfPath=(String) request.getAttribute("ConfigurationFile");
			// File fileXML = new File(ConfPath+"FrogRelativePath.xml");
			
			//ANDREA String ConfPath=(String) request.getAttribute("ConfigurationFile") is setted in this routine at line 142. So now we can't use this. 

			System.out.println("directory home = " + System.getProperty("catalina.base"));

			File fileXML = new File(System.getProperty("catalina.base")+"/webapps/ROOT/WEB-INF/classes/FrogRelativePath.xml");
			DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
			DocumentBuilder dBuilder;
			Document doc=null;
			try {
				dBuilder = dbFactory.newDocumentBuilder();
				doc = dBuilder.parse(fileXML);
			} catch (ParserConfigurationException e1) {
				e1.printStackTrace();
			} catch (SAXException e) {
				e.printStackTrace();
			}
			
			doc.getDocumentElement().normalize();			
			
			NodeList nodes = doc.getElementsByTagName("absolute_path_frog");
			Node node = nodes.item(0);
			Element element = (Element) node;
			NodeList nodes2 = element.getElementsByTagName("url").item(0).getChildNodes();
			Node node2 = (Node) nodes2.item(0);
						
			String confPath = node2.getNodeValue() + "/web/LocalServer/conf/";
			request.setAttribute("ConfigurationFile", confPath);

			InputStream stream = request.getServletContext().getResourceAsStream("/WEB-INF/salt");
			BufferedReader in = new BufferedReader(new InputStreamReader(stream));

			request.setAttribute("salt", in.readLine());
			chain.doFilter(request, response);
			//tx.commit();

		} catch (Throwable ex) {
			ex.printStackTrace();
			//if (tx!=null) tx.rollback();
		} finally {
			//s.close();
		}

	}

	/**
	 * @see Filter#init(FilterConfig)
	 */
	@SuppressWarnings("deprecation")
	public void init(FilterConfig fConfig) throws ServletException {

		//Configuration conf = new Configuration();
		//conf.configure();


		//String db_url = conf.getProperty("hibernate.connection.url");
		//String username = conf.getProperty("hibernate.connection.username");
		//String passwd = conf.getProperty("hibernate.connection.password");

		CleanDB=new Timer();
		CheckUsers=new Timer();
		CheckTempUsers=new Timer();
		CheckMgmt=new Timer();
		
		CheckMgmt.schedule(new timer.CheckMgmt(), new Date(), 1000*60);
		
		//System.out.println("Database info:" + db_url + " user: " + "passwd: "+ passwd);
		//CheckTempUsers.schedule(new CleanTempUsersTask(), new Date(), 1000*60*4); // removes temporary new users that not confirms the registration
		//CleanDB.schedule(new CleanDBTask(db_url, username, passwd), new Date(), 1000*60); // removes PEX from RunningPEX when the PEX is shut down in a wrong way   
		//CheckUsers.schedule(new CheckUsersTask(), new Date(), ((long) 1000*60*60*24*365));  // removes the user that doesn't login for 365 days

		
		//factory= conf.buildSessionFactory();
	
	}

}
