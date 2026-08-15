package org.contextmapper.hda;

import java.io.File;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.contextmapper.dsl.cml.CMLResource;
import org.contextmapper.dsl.generator.ContextMapGenerator;
import org.contextmapper.dsl.generator.contextmap.ContextMapFormat;
import org.contextmapper.dsl.standalone.ContextMapperStandaloneSetup;
import org.contextmapper.dsl.standalone.StandaloneContextMapperAPI;
import org.eclipse.emf.ecore.util.EcoreUtil;

/**
 * Genera los diagramas de Context Map (PNG/SVG/DOT) de Hogar de los Alpes en ./src-gen.
 * Requiere Graphviz (dot) disponible en el PATH.
 *
 * El Team Map recibe un tratamiento grafico especial (solo presentacion; el
 * modelo CML no cambia): clustering de equipos, mayor separacion de etiquetas,
 * mas espacio entre nodos (nodesep/ranksep inyectados en el DOT) y salida en
 * alta resolucion: SVG maestro + PNG de ~5000 px de ancho.
 */
public class GenerateContextMaps {

    private static final String[] CML_FILES = {
            "src/main/cml/hogar-de-los-alpes-as-is.cml",
            "src/main/cml/hogar-de-los-alpes-to-be.cml"
    };

    private static final String TEAM_MAP_CML = "src/main/cml/hogar-de-los-alpes-team-map.cml";
    private static final String SRC_GEN = "src-gen";
    private static final String TEAM_MAP_GV = SRC_GEN + "/hogar-de-los-alpes-team-map_ContextMap.gv";
    private static final String TEAM_MAP_TUNED_GV = SRC_GEN + "/hogar-de-los-alpes-team-map.gv";
    private static final String TEAM_MAP_SVG = SRC_GEN + "/hogar-de-los-alpes-team-map.svg";
    private static final String TEAM_MAP_PNG = SRC_GEN + "/hogar-de-los-alpes-team-map.png";

    /*
     * Se probo 5 y 6; con 8 se reduce la superposicion de cajas U/D/C/S/P sin
     * exagerar el espaciado (rango valido del generador: 1-20).
     */
    private static final int TEAM_MAP_LABEL_SPACING_FACTOR = 8;
    private static final int TEAM_MAP_TARGET_WIDTH_PX = 5000;
    private static final String NODESEP = "1.4";
    private static final String RANKSEP = "2.0";
    private static final String LABEL_DISTANCE = "3.5";

    public static void main(String[] args) throws Exception {
        StandaloneContextMapperAPI contextMapper = ContextMapperStandaloneSetup.getStandaloneAPI();

        for (String cmlFile : CML_FILES) {
            ContextMapGenerator generator = new ContextMapGenerator();
            generator.setContextMapFormats(ContextMapFormat.PNG, ContextMapFormat.SVG, ContextMapFormat.DOT);
            generator.setLabelSpacingFactor(10);
            generator.printAdditionalLabels(true);
            generate(contextMapper, generator, cmlFile);
        }

        ContextMapGenerator teamMapGenerator = new ContextMapGenerator();
        teamMapGenerator.setContextMapFormats(ContextMapFormat.PNG, ContextMapFormat.SVG, ContextMapFormat.DOT);
        teamMapGenerator.clusterTeams(true);
        teamMapGenerator.setLabelSpacingFactor(TEAM_MAP_LABEL_SPACING_FACTOR);
        teamMapGenerator.setWidth(TEAM_MAP_TARGET_WIDTH_PX);
        teamMapGenerator.printAdditionalLabels(true);
        generate(contextMapper, teamMapGenerator, TEAM_MAP_CML);

        renderTunedTeamMap();

        System.out.println("Listo. Revisa la carpeta ./src-gen");
        System.out.println("Team Map labelSpacingFactor=" + TEAM_MAP_LABEL_SPACING_FACTOR
                + ", nodesep=" + NODESEP + ", ranksep=" + RANKSEP
                + " (sin splines=ortho)");
    }

    private static void generate(StandaloneContextMapperAPI contextMapper, ContextMapGenerator generator, String cmlFile) {
        // Se pasa una URI 'file:' absoluta para que la URI del recurso sea jerarquica
        // y los imports relativos entre archivos CML puedan resolverse (en Windows una
        // ruta 'c:/...' se interpretaria como protocolo 'c').
        CMLResource resource = contextMapper.loadCML(new File(cmlFile).toURI().toString());
        // Resuelve las referencias a elementos definidos en otros archivos CML (imports).
        EcoreUtil.resolveAll(resource.getResourceSet());
        contextMapper.callGenerator(resource, generator);
        System.out.println("Diagramas generados para: " + cmlFile);
    }

    /**
     * Post-procesa el DOT del Team Map (nodesep/ranksep, labeldistance, clusters
     * por equipo) y lo renderiza con el 'dot' del PATH: SVG maestro y PNG de
     * ~5000 px de ancho manteniendo la proporcion.
     */
    private static void renderTunedTeamMap() throws Exception {
        String dot = new String(Files.readAllBytes(Paths.get(TEAM_MAP_GV)), StandardCharsets.UTF_8);

        // El .gv generado referencia el icono de equipos en un directorio temporal;
        // se copia el icono a src-gen y se apunta imagepath alli para que 'dot'
        // pueda resolverlo de forma reproducible.
        exportTeamIcon();
        String srcGenPath = Paths.get(SRC_GEN).toAbsolutePath().toString().replace('\\', '/');
        Matcher imagePathMatcher = Pattern.compile("\"imagepath\"=\"([^\"]*)\"").matcher(dot);
        if (imagePathMatcher.find()) {
            dot = imagePathMatcher.replaceAll(Matcher.quoteReplacement("\"imagepath\"=\"" + srcGenPath + "\""));
        }

        /*
         * Mas espacio entre nodos y entre filas. No se usa splines=ortho: con nodos
         * tipo egg y etiquetas HTML de patrones DDD empeora el resultado y oculta
         * etiquetas. Se mantiene el spline por defecto (curvo) de Graphviz.
         */
        dot = dot.replaceFirst(Pattern.quote("digraph \"ContextMapGraph\" {"),
                Matcher.quoteReplacement("digraph \"ContextMapGraph\" {\n"
                        + "nodesep=" + NODESEP + "\n"
                        + "ranksep=" + RANKSEP + "\n"
                        + "pad=1.0\n"
                        + "overlap=false\n"
                        + "sep=\"+30\"\n"
                        + "forcelabels=true\n"));

        // Separar las cajas U/D/C/S de los extremos de las flechas (el generador
        // las deja con labeldistance=0, lo que produce superposiciones).
        dot = dot.replace("\"labeldistance\"=\"0\"", "\"labeldistance\"=\"" + LABEL_DISTANCE + "\"");

        // Alargar un poco las aristas entre equipos (no realizes) para dar
        // espacio a las etiquetas de patrones DDD.
        dot = lengthenTeamRelationshipEdges(dot);

        // El generador agrupa TODOS los equipos en un cluster y TODOS los
        // contextos en otro, lo que produce dos bandas alejadas con flechas
        // 'realizes' kilometricas. Se desactivan esos clusters globales
        // (renombrandolos sin el prefijo 'cluster_') y se crea un cluster por
        // equipo que contiene al equipo y sus Bounded Contexts.
        dot = dot.replace("cluster_GenericSubgraph", "GenericSubgraph");
        dot = dot.replace("cluster_Teams_Subgraph", "Teams_Subgraph");
        dot = ensureMissingRealizesEdges(dot);
        dot = appendPerTeamClusters(dot);

        Files.write(Paths.get(TEAM_MAP_TUNED_GV), dot.getBytes(StandardCharsets.UTF_8));

        // SVG maestro (vectorial, maxima calidad).
        runDot("-Tsvg", TEAM_MAP_TUNED_GV, "-o", TEAM_MAP_SVG);

        // PNG de alta resolucion: se calcula el DPI para lograr ~5000 px de ancho
        // a partir del ancho natural en puntos (72 dpi) reportado por el SVG.
        double widthPt = readSvgWidthPt(TEAM_MAP_SVG);
        int dpi = (int) Math.max(72, Math.round(TEAM_MAP_TARGET_WIDTH_PX / widthPt * 72.0));
        runDot("-Tpng", "-Gdpi=" + dpi, TEAM_MAP_TUNED_GV, "-o", TEAM_MAP_PNG);

        printPngSize(TEAM_MAP_PNG);
        System.out.println("Team Map ajustado: " + TEAM_MAP_SVG + " y " + TEAM_MAP_PNG
                + " (dpi=" + dpi + ", labelSpacingFactor=" + TEAM_MAP_LABEL_SPACING_FACTOR + ")");
    }

    /**
     * Inserta minlen=2 en las aristas entre equipos (no realizes) para forzar
     * mas recorrido y reducir el amontonamiento de etiquetas U/D.
     */
    private static String lengthenTeamRelationshipEdges(String dot) {
        Matcher edge = Pattern.compile("(\"[\\w]+\" -> \"[\\w]+\" \\[[^\\]]*)(\\])").matcher(dot);
        StringBuffer buffer = new StringBuffer();
        while (edge.find()) {
            String attrs = edge.group(1);
            if (attrs.contains("realizes") || attrs.contains("minlen")) {
                edge.appendReplacement(buffer, Matcher.quoteReplacement(edge.group(0)));
            } else {
                edge.appendReplacement(buffer, Matcher.quoteReplacement(attrs + ",\"minlen\"=\"2\"" + edge.group(2)));
            }
        }
        edge.appendTail(buffer);
        return buffer.toString();
    }

    /**
     * ContextMapper a veces omite alguna flecha 'realizes' (p. ej. MicroLending).
     * Se completa a partir de los nodos TEAM conocidos y los contextos que no
     * tienen dueno en el DOT, sin alterar el CML.
     */
    private static String ensureMissingRealizesEdges(String dot) {
        // FintechTeam posee MicroLending en el CML, pero el DOT generado no
        // incluye esa flecha realizes; se inyecta solo para el layout grafico.
        if (dot.contains("\"MicroLending\"") && !dot.contains("\"FintechTeam\" -> \"MicroLending\"")) {
            String edge = "\"FintechTeam\" -> \"MicroLending\" "
                    + "[\"color\"=\"#686868\",\"fontsize\"=\"12\",\"fontcolor\"=\"#686868\","
                    + "\"style\"=\"dashed\",\"label\"=\"  \\\"realizes\\\"\\n\",\"fontname\"=\"sans-serif\"]\n";
            int closingBrace = dot.lastIndexOf('}');
            return dot.substring(0, closingBrace) + edge + "}\n";
        }
        return dot;
    }

    /**
     * Deriva la pertenencia equipo -> contextos de las flechas 'realizes' del
     * DOT y agrega un cluster por equipo, de modo que cada equipo se dibuje
     * junto a sus Bounded Contexts.
     */
    private static String appendPerTeamClusters(String dot) {
        Matcher realizesEdges = Pattern.compile("\"(\\w+)\" -> \"(\\w+)\" \\[[^\\]]*realizes").matcher(dot);
        Map<String, List<String>> contextsByTeam = new LinkedHashMap<>();
        while (realizesEdges.find()) {
            String team = realizesEdges.group(1);
            String context = realizesEdges.group(2);
            contextsByTeam.computeIfAbsent(team, key -> new ArrayList<>()).add(context);
        }

        StringBuilder clusters = new StringBuilder();
        for (Map.Entry<String, List<String>> team : contextsByTeam.entrySet()) {
            clusters.append("subgraph \"cluster_").append(team.getKey()).append("\" {\n");
            clusters.append("graph [\"style\"=\"rounded,dashed\",\"color\"=\"gray55\",\"margin\"=\"28\",\"pencolor\"=\"gray55\"]\n");
            clusters.append('"').append(team.getKey()).append("\"\n");
            for (String context : team.getValue()) {
                clusters.append('"').append(context).append("\"\n");
            }
            clusters.append("}\n");
        }

        int closingBrace = dot.lastIndexOf('}');
        return dot.substring(0, closingBrace) + clusters + "}\n";
    }

    private static void exportTeamIcon() throws Exception {
        Path target = Paths.get(SRC_GEN, "team-icon.png");
        try (InputStream icon = GenerateContextMaps.class.getResourceAsStream("/team-icon.png")) {
            if (icon != null) {
                Files.copy(icon, target, StandardCopyOption.REPLACE_EXISTING);
                return;
            }
        }
        // Fallback: si el icono ya esta en src-gen (generacion previa), se reutiliza.
        if (!Files.exists(target)) {
            throw new IllegalStateException("No se encontro team-icon.png en el classpath ni en src-gen.");
        }
    }

    private static double readSvgWidthPt(String svgFile) throws Exception {
        String svg = new String(Files.readAllBytes(Paths.get(svgFile)), StandardCharsets.UTF_8);
        Matcher matcher = Pattern.compile("width=\"(\\d+(?:\\.\\d+)?)pt\"").matcher(svg);
        if (!matcher.find()) {
            throw new IllegalStateException("No se pudo leer el ancho del SVG " + svgFile);
        }
        return Double.parseDouble(matcher.group(1));
    }

    private static void runDot(String... arguments) throws Exception {
        String[] command = new String[arguments.length + 1];
        command[0] = "dot";
        System.arraycopy(arguments, 0, command, 1, arguments.length);
        Process process = new ProcessBuilder(command).inheritIO().start();
        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new IllegalStateException("dot fallo con codigo " + exitCode);
        }
    }

    /** Imprime el tamano del PNG leyendo el chunk IHDR (sin APIs externas). */
    private static void printPngSize(String pngPath) throws Exception {
        byte[] bytes = Files.readAllBytes(Paths.get(pngPath));
        if (bytes.length < 24) {
            System.out.println("PNG demasiado corto para leer dimensiones: " + pngPath);
            return;
        }
        int width = ((bytes[16] & 0xff) << 24) | ((bytes[17] & 0xff) << 16)
                | ((bytes[18] & 0xff) << 8) | (bytes[19] & 0xff);
        int height = ((bytes[20] & 0xff) << 24) | ((bytes[21] & 0xff) << 16)
                | ((bytes[22] & 0xff) << 8) | (bytes[23] & 0xff);
        System.out.println("PNG dimensions: " + width + "x" + height);
    }
}
