/************************************************************************************
*																					*
*     Copyright notice: please read file license.txt in the project root folder.    *
*                                              								     	*
************************************************************************************/

package log.impl;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.logging.Formatter;
import java.util.logging.Handler;
import java.util.logging.Level;
import java.util.logging.LogRecord;

/**
 * @see CustomHtmlFormatter
 * @author christian.meyer
 * @author crmdevelopment
 * @version 1.0, November 2010
 */

public class CustomHTMLFormatter extends Formatter
{

	private int row;

	// This method is called for every log records
	public String format(LogRecord rec)
	{
		StringBuffer buf = new StringBuffer(1000);
		buf.append("<tr>");
		//Here we use an alternate background color for every 2nd row (just to improve readability)
		if(row%2==0)
			buf.append("<tr>");
		else
			buf.append("<tr bgcolor = #C0C0C0>");

		buf.append("<td>");
		buf.append(getFormattedDate(rec.getMillis()));
		buf.append("</td>");
		buf.append("<td>");
		buf.append(rec.getSourceClassName()+"."+rec.getSourceMethodName());
		buf.append("</td>");
		buf.append("<td>");

		// Set the font color for levels >= WARNING to red
		if (rec.getLevel().intValue() >= Level.WARNING.intValue()){
			buf.append("<font color=\"#FF0000\">");
		}

		buf.append(rec.getLevel());
		buf.append("</td>");
		buf.append("<td>");
		buf.append(formatMessage(rec));

		//This happens if we get a throwable: we're iterating through the
		//stacktrace & printing everything nicely formatted
		if(rec.getThrown()!=null){
			buf.append("<font color=\"#FF0000\">");
			buf.append(": " + "<a href=\"http://www.google.de/search?q=" + rec.getThrown() +
					"\" title= \"Search at Google\" target=\"_blank\">" + rec.getThrown() + "</a><br>");

			StackTraceElement[] stackTrace = rec.getThrown().getStackTrace();
			for (StackTraceElement element : stackTrace)
			{
				String exceptionMsg = "at " + element.getClassName() +
						" (" + element.getMethodName() + ":" +
						element.getLineNumber() + ")<br>";
				buf.append(exceptionMsg);
			}
		}

		buf.append('\n');
		buf.append("</td>");
		buf.append("</tr>\n");
		row++;
		return buf.toString();
	}

	private String getFormattedDate(long millisecs)
	{
		SimpleDateFormat date_format = new SimpleDateFormat("HH:mm:ss.SSS");
		Date resultdate = new Date(millisecs);
		return date_format.format(resultdate);
	}

	// This method creates the basic HTML structure. You can add your own
	// CSS after the <style type="text/css"> tag
	public String getHead(Handler h)
	{
		return "<HTML>\n<HEAD><title>Datamasker logfile</title>\n" +
				"<link rel=\"stylesheet\" type=\"text/css\" href=\"datamasker.css\" />" +
				"<style type=\"text/css\">\n" +
				"caption {font-size: 1.7em; color: #F06; text-align: left;}\n" +
				"heading {font-family: Arial; font-size: medium; color: #555; text-decoration:underline; font-weight: bold; text-align: center }\n" +
				"footer {font-family: Arial; font-size: x-small; color: #555; text-align: right }\n" +
				"body {font-family: Arial; font-size: small; color: black; text-align: left }\n" +
				"table {margin: 0; padding: 0; border-collapse: collapse; width: 100%;}\n" +
				"td, th {padding: 1px 4px; border-bottom: 1px solid #EEE;}\n" +
				"td + td {border-left: 1px solid #FAFAFA; color: #999;}\n" +
				"td + td + td {color: #666; border-left: none;}\n" +
				"td a {color: #444; text-decoration: none; text-align: left;}\n" +
				"td a, th a {display: block; width: 100%;}\n" +
				"td a:hover {background: #444; color: #FFF;}\n" +
				"tfoot th {text-align: left;}\n" +
				"th {text-align: left;}\n" +
				"th + th {text-align: left;}\n" +
				"th + th + th {text-align: left;}\n" +
				"th a {color: #F06; text-decoration: none; font-size: 1.1em;}\n" +
				"th a:visited {color: #F69;}\n" +
				"th a:hover {color: #F06; text-decoration: underline;}\n" +
				"thead tr, tfoot tr {color: #555; font-size: 0.8em;}\n" +
				"tr {font: 12px sans-serif; background: repeat-x #F8F8F8; color: #666;}\n" +
				"tr:hover {background: #FFF;}\n" +
				"</style>\n" +
				"<meta http-equiv=\"refresh\" content=\"5\" />"+
				"</HEAD>\n" +
				"<BODY>\n" +
				"<heading>Datamasker Logfile: " + (new Date()) +"</heading><br>\n<br>" +
				"\n<PRE>\n" +
				"<table rules=\"all\"; cellpadding=\"2px\">\n " +
				"<tr bgcolor = #A9A9A9><th>Time</th><th>Source</th><th>Type</th><th>Message</th></tr>\n";
	}

	// This method appends the necessary closing tags
	public String getTail(Handler h)
	{
		return "</table>\n</PRE>\n <footer></footer> \n </BODY>\n</HTML>\n";
	}
}

