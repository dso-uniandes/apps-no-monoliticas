package org.contextmapper.hda;

import org.contextmapper.dsl.cml.CMLResource;
import org.contextmapper.dsl.generator.ContextMapGenerator;
import org.contextmapper.dsl.generator.contextmap.ContextMapFormat;
import org.contextmapper.dsl.standalone.ContextMapperStandaloneSetup;
import org.contextmapper.dsl.standalone.StandaloneContextMapperAPI;
import org.eclipse.emf.ecore.util.EcoreUtil;

/**
 * Genera los diagramas de Context Map (PNG/SVG/DOT) de Hogar de los Alpes en ./src-gen
 * Requiere Graphviz (dot) disponible en el PATH
 */
public class GenerateContextMaps {

    private static final String[] CML_FILES = {
            "src/main/cml/hogar-de-los-alpes-as-is.cml",
            "src/main/cml/hogar-de-los-alpes-to-be.cml",
            "src/main/cml/hogar-de-los-alpes-team-map.cml"
    };

    public static void main(String[] args) {
        StandaloneContextMapperAPI contextMapper = ContextMapperStandaloneSetup.getStandaloneAPI();
        for (String cmlFile : CML_FILES) {
            ContextMapGenerator generator = new ContextMapGenerator();
            generator.setContextMapFormats(ContextMapFormat.PNG, ContextMapFormat.SVG, ContextMapFormat.DOT);
            generator.setLabelSpacingFactor(10);
            generator.printAdditionalLabels(true);
            CMLResource resource = contextMapper.loadCML(new java.io.File(cmlFile).toURI().toString());
            EcoreUtil.resolveAll(resource.getResourceSet());
            contextMapper.callGenerator(resource, generator);
            System.out.println("Diagramas generados para: " + cmlFile);
        }
        System.out.println("Listo. Revisa la carpeta ./src-gen");
    }
}
