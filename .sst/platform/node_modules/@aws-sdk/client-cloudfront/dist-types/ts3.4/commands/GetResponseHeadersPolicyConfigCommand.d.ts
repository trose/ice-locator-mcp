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
  GetResponseHeadersPolicyConfigRequest,
  GetResponseHeadersPolicyConfigResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetResponseHeadersPolicyConfigCommandInput
  extends GetResponseHeadersPolicyConfigRequest {}
export interface GetResponseHeadersPolicyConfigCommandOutput
  extends GetResponseHeadersPolicyConfigResult,
    __MetadataBearer {}
export declare class GetResponseHeadersPolicyConfigCommand extends $Command<
  GetResponseHeadersPolicyConfigCommandInput,
  GetResponseHeadersPolicyConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetResponseHeadersPolicyConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetResponseHeadersPolicyConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetResponseHeadersPolicyConfigCommandInput,
    GetResponseHeadersPolicyConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
