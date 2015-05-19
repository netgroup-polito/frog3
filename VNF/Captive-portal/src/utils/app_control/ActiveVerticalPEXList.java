package utils.app_control;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

import javax.servlet.ServletContext;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;









import utils.login.HashTabValue;

/**
 * Servlet implementation class ActiveVerticalPEXList
 */
@WebServlet("/ActiveVerticalPEXList")
public class ActiveVerticalPEXList extends HttpServlet {
	private static final long serialVersionUID = 1L;
       
    /**
     * @see HttpServlet#HttpServlet()
     */
    public ActiveVerticalPEXList() {
        super();
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	@SuppressWarnings({ "unchecked", "rawtypes" })
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		System.out.println("INFO: Executing servlet_ActiveVerticalPEX...");
		PrintWriter out = response.getWriter();
		String string_out=new String();
		string_out="";
		String user=request.getParameter("user");
		ServletContext context = getServletContext();
		Hashtable<Integer, HashTabValue> VertPEX=(Hashtable<Integer, HashTabValue>)context.getAttribute("HashTab");
		Map<Integer,HashTabValue> sortedMap=null;
		
		if(VertPEX!=null){
			
			sortedMap= new TreeMap<Integer, HashTabValue>(VertPEX);
			
			Set s=sortedMap.entrySet();
			Iterator it=s.iterator();
			
			while(it.hasNext()){
				
				Map.Entry m=(Map.Entry)it.next();
				HashTabValue mm=new HashTabValue();
				mm=(HashTabValue)m.getValue();
				
				if( mm.getValue1().equals(user) || user.equals("admin")){
				if(mm.getValue2().matches("^([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})$")){//per evitare rimozione PEX inserire controllo con TIMESTAMP
					System.out.println("chiave:"+m.getKey()+" Valore1:"+mm.getValue1()+" Valore2:"+mm.getValue2());
					string_out+="'id':'"+m.getKey()+"',";
					string_out+="'user':'"+mm.getValue1()+"',";
					string_out+="'MAC':'"+mm.getValue2()+"'},\n";
				}
}
				//System.out.println("chiave:"+m.getKey()+" Valore1:"+mm.getValue1()+" Valore2:"+mm.getValue2());
				
			}
			
		}

		
		out.print(string_out);
		
		System.out.println("INFO: ...servlet_ActiveVerticalPEX executed.");
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	@SuppressWarnings({ "rawtypes", "unchecked" })
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		System.out.println("INFO: Executing servlet_ActiveVerticalPEX...");
		PrintWriter out = response.getWriter();
		String string_out=new String();
		string_out="";
		
		
		ServletContext context = getServletContext();
		Hashtable<Integer, HashTabValue> VertPEX=(Hashtable<Integer, HashTabValue>)context.getAttribute("HashTab");
		Map<Integer,HashTabValue> sortedMap=null;
if(VertPEX!=null){
			
			sortedMap= new TreeMap<Integer, HashTabValue>(VertPEX);
			
			Set s=sortedMap.entrySet();
			Iterator it=s.iterator();
			
			while(it.hasNext()){
				
				Map.Entry m=(Map.Entry)it.next();
				HashTabValue mm=new HashTabValue();
				mm=(HashTabValue)m.getValue();
				
				
				if(mm.getValue2().matches("^([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})$")){//per evitare rimozione PEX inserire controllo con TIMESTAMP
					System.out.println("chiave:"+m.getKey()+" Valore1:"+mm.getValue1()+" Valore2:"+mm.getValue2());
					string_out+="'id':'"+m.getKey()+"',";
					string_out+="'user':'"+mm.getValue1()+"',";
					string_out+="'MAC':'"+mm.getValue2()+"'},\n";
				}
				
				//System.out.println("chiave:"+m.getKey()+" Valore1:"+mm.getValue1()+" Valore2:"+mm.getValue2());
				
			}
			
		}
		
		
		
		
		
		
		
		out.print(string_out);
		
		System.out.println("INFO: ...servlet_ActiveVerticalPEX executed.");
	}

}
