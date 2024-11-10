package com.week12;

import java.io.*;
import javax.servlet.ServletException;
import javax.servlet.http.*;
import javax.servlet.annotation.*;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

@WebServlet("/result") 
public class ResultServlet extends HttpServlet {

    // POST 요청
    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        processRequest(request, response);
    }

    // GET 요청
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        processRequest(request, response);
    }

    // 공통
    private void processRequest(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        response.setContentType("text/html; charset=UTF-8");
        request.setCharacterEncoding("UTF-8");

        String userInput = request.getParameter("userInput");

        // log4j 사용하여 error로 로깅
        Logger logger = LogManager.getLogger(ResultServlet.class);
        logger.error("userInput : " + userInput);

        PrintWriter out = response.getWriter();
        out.println("<html><body>");
        out.println("<h2>입력값 : " + (userInput != null ? userInput : "없음") + "</h2>");
        out.println("<br><a href='index.jsp'>처음으로</a>");
        out.println("</body></html>");
    }
}
