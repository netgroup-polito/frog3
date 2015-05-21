

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.OutputStream;

import javax.servlet.ServletContext;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Servlet implementation class CommonServlet
 */
@WebServlet("/CommonServlet")
public class CommonServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;
       
    /**
     * @see HttpServlet#HttpServlet()
     */
    public CommonServlet() {
        super();
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		FileInputStream in=null;
		OutputStream out=null;		 
	
		try{ 
			ServletContext sc = getServletContext();  
			String path=req.getRequestURI().substring(req.getContextPath().length()+1, req.getRequestURI().length());  
			String filename = sc.getRealPath(path);  

			// Get the MIME type of the file  
			String mimeType = sc.getMimeType(filename);  
			if (mimeType == null) {  
				sc.log("Could not get MIME type of "+filename);  
				
				//can be that the file does not exists
				resp.setHeader("Cache-Control","no-cache"); //HTTP 1.1
				resp.setHeader("Pragma","no-cache"); //HTTP 1.0
				resp.setDateHeader ("Expires", 0); //prevents caching at the proxy server
				resp.sendRedirect("http://"+req.getLocalAddr()+"/login.jsp");  				  
			}  
			else{
				// Set content type  
				resp.setContentType(mimeType);  
	
				// Set content size  
				File file = new File(filename);  
				resp.setContentLength((int)file.length());  
	
				// Open the file and output streams  
				in = new FileInputStream(file);  
				out = resp.getOutputStream();  
	
				// Copy the contents of the file to the output stream  
				byte[] buf = new byte[1024];  
				int count = 0;  
				while ((count = in.read(buf)) >= 0) {  
					out.write(buf, 0, count);  
				}
			}
		}catch(Exception exc){
			System.out.println("INFO Managed exception: "+exc.getMessage());
			resp.setHeader("Cache-Control","no-cache"); //HTTP 1.1
			resp.setHeader("Pragma","no-cache"); //HTTP 1.0
			resp.setDateHeader ("Expires", 0); //prevents caching at the proxy server
			resp.sendRedirect("http://"+req.getLocalAddr()+"/login.jsp");

		}finally{
			if (in!=null)
				in.close();  
			if (out!=null)
				out.close();  
		}
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
	}

}
