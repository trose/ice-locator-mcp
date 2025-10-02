import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  ListCloudFrontOriginAccessIdentitiesRequest,
  ListCloudFrontOriginAccessIdentitiesResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListCloudFrontOriginAccessIdentitiesCommandInput
  extends ListCloudFrontOriginAccessIdentitiesRequest {}
export interface ListCloudFrontOriginAccessIdentitiesCommandOutput
  extends ListCloudFrontOriginAccessIdentitiesResult,
    __MetadataBearer {}
export declare class ListCloudFrontOriginAccessIdentitiesCommand extends $Command<
  ListCloudFrontOriginAccessIdentitiesCommandInput,
  ListCloudFrontOriginAccessIdentitiesCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListCloudFrontOriginAccessIdentitiesCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListCloudFrontOriginAccessIdentitiesCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    ListCloudFrontOriginAccessIdentitiesCommandInput,
    ListCloudFrontOriginAccessIdentitiesCommandOutput
  >;
  private serialize;
  private deserialize;
}
